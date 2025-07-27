import os
import logging
import requests
import time
from datetime import datetime
import schedule
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import telebot
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("./logs/bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Get token from environment variable
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')

# Initialize the bot
bot = telebot.TeleBot(TOKEN)

def setup_webdriver(max_retries=5, retry_delay=2):
    """Configure and return a remote Chrome WebDriver instance with retries"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=5400,2950")
    chrome_options.add_argument("--force-device-scale-factor=2")
    
    selenium_host = os.getenv('SELENIUM_HOST', 'localhost')
    selenium_port = os.getenv('SELENIUM_PORT', '4444')
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Connecting to Selenium at http://{selenium_host}:{selenium_port}/wd/hub (attempt {attempt+1}/{max_retries})")
            driver = webdriver.Remote(
                command_executor=f'http://{selenium_host}:{selenium_port}/wd/hub',
                options=chrome_options
            )
            logger.info("Successfully connected to Selenium")
            return driver
        except Exception as e:
            logger.warning(f"Failed to connect to Selenium: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Max retries exceeded. Could not connect to Selenium.")
                raise

def get_crypto_price(symbol):
    """Fetch the current crypto price from CoinGecko API"""
    try:
        # Map common symbols to CoinGecko IDs
        symbol_map = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'BNB': 'binancecoin',
            'ADA': 'cardano',
            'SOL': 'solana',
            'XRP': 'ripple',
            'DOT': 'polkadot',
            'DOGE': 'dogecoin',
            'AVAX': 'avalanche-2',
            'MATIC': 'matic-network'
        }
        
        coin_id = symbol_map.get(symbol, symbol.lower())
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            price = data.get(coin_id, {}).get('usd')
            if price:
                return f"${price:,.2f}"
        
        return None
    except Exception as e:
        logger.error(f"Error fetching {symbol} price: {e}")
        return None

def capture_coinglass_heatmap(symbol="BTC", time_period="24 hour"):
    """
    Capture the Coinglass liquidation heatmap
    
    Args:
        symbol (str): Cryptocurrency symbol (e.g., "BTC", "ETH")
        time_period (str): Time period to select (e.g., "24 hour", "1 month", "3 month")
    """
    driver = None
    try:
        logger.info(f"Starting capture of Coinglass {symbol} heatmap with {time_period} timeframe")
        driver = setup_webdriver()
        
        # Navigate to Coinglass liquidation page
        driver.get("https://www.coinglass.com/pro/futures/LiquidationHeatMap")
        wait = WebDriverWait(driver, 20)
        
        # Optimize page for screenshot
        driver.execute_script("""
            var style = document.createElement('style');
            style.innerHTML = `
                * {
                    transition: none !important;
                    animation: none !important;
                }
                .echarts-for-react {
                    width: 100% !important;
                    height: 100% !important;
                }
                canvas {
                    image-rendering: -webkit-optimize-contrast !important;
                    image-rendering: crisp-edges !important;
                }
            `;
            document.head.appendChild(style);
            window.devicePixelRatio = 2;
        """)
        
        # Select symbol first
        symbol_selector = "#__next > div:nth-child(2) > div > div.prolayoutBox.MuiBox-root.cg-style-1rr4qq7 > div.prolayout.MuiBox-root.cg-style-0 > div.plr20 > div.MuiBox-root.cg-style-uwwqev > div.dfsb.MuiBox-root.cg-style-0 > div > div > div.MuiAutocomplete-root.MuiAutocomplete-hasPopupIcon.MuiAutocomplete-variantOutlined.MuiAutocomplete-colorNeutral.MuiAutocomplete-sizeMd.font2.cg-style-phfqk"
        
        try:
            # Use JavaScript to directly set the symbol and trigger updates
            driver.execute_script(f"""
                var input = document.querySelector('{symbol_selector} input');
                if (input) {{
                    input.value = '{symbol}';
                    input.focus();
                    
                    var inputEvent = new Event('input', {{ bubbles: true, cancelable: true }});
                    var changeEvent = new Event('change', {{ bubbles: true, cancelable: true }});
                    var focusEvent = new Event('focus', {{ bubbles: true, cancelable: true }});
                    var blurEvent = new Event('blur', {{ bubbles: true, cancelable: true }});
                    
                    input.dispatchEvent(focusEvent);
                    input.dispatchEvent(inputEvent);
                    input.dispatchEvent(changeEvent);
                    
                    setTimeout(function() {{
                        input.dispatchEvent(blurEvent);
                    }}, 500);
                }}
            """)
            time.sleep(3)
            
            # Verify the symbol was actually set
            current_value = driver.execute_script(f"return document.querySelector('{symbol_selector} input').value;")
            logger.info(f"Symbol input value after setting: {current_value}")
            
            # Wait for chart to update with new symbol data
            time.sleep(5)
            logger.info(f"Set symbol to: {symbol}")
        except Exception as symbol_e:
            logger.warning(f"Could not select symbol {symbol}: {symbol_e}")
        
        # Find and click the time period dropdown button
        time_dropdown = wait.until(EC.element_to_be_clickable((
            By.CSS_SELECTOR, "div.MuiSelect-root button.MuiSelect-button"
        )))
        
        if time_dropdown.text.strip() != time_period:
            time_dropdown.click()
            time.sleep(2)
            
            driver.execute_script(f"""
                var options = document.querySelectorAll('li[role="option"]');
                for(var i = 0; i < options.length; i++) {{
                    if(options[i].textContent.includes('{time_period}')) {{
                        options[i].click();
                        break;
                    }}
                }}
            """)
            time.sleep(3)
        
        # Find and capture the chart
        try:
            heatmap_container = wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, "div.echarts-for-react"
            )))
        except Exception:
            heatmap_container = wait.until(EC.presence_of_element_located((
                By.XPATH, "//div[contains(@class, 'echarts-for-react')]"
            )))
        
        time.sleep(3)
        
        rect = driver.execute_script("""
            var rect = arguments[0].getBoundingClientRect();
            return {
                x: rect.left,
                y: rect.top,
                width: rect.width,
                height: rect.height
            };
        """, heatmap_container)
        
        # Capture screenshot with CDP
        result = driver.execute_cdp_cmd('Page.captureScreenshot', {
            'clip': {
                'x': rect['x'],
                'y': rect['y'],
                'width': rect['width'],
                'height': rect['height'],
                'scale': 2
            },
            'captureBeyondViewport': True,
            'fromSurface': True
        })
        
        png_data = base64.b64decode(result['data'])
        image = Image.open(BytesIO(png_data))
        
        temp_file = f"{symbol.lower()}_liquidation_heatmap_{datetime.now().strftime('%Y%m%d')}_{time_period.replace(' ', '_')}.png"
        image.save(temp_file, format='PNG', optimize=True, quality=100)
        
        logger.info(f"Heatmap captured and saved as {temp_file}")
        return temp_file
        
    except Exception as e:
        logger.error(f"Error capturing heatmap: {e}")
        return None
    finally:
        if driver:
            driver.quit()

@bot.message_handler(commands=['map'])
def handle_map_command(message):
    """Handle /map command with symbol and timeframe"""
    try:
        parts = message.text.split()
        
        if len(parts) < 2:
            bot.reply_to(message, "Usage: /map <SYMBOL> [TIMEFRAME]\nExample: /map BTC 24 hour")
            return
        
        symbol = parts[1].upper()
        timeframe = " ".join(parts[2:]) if len(parts) > 2 else "24 hour"
        
        valid_timeframes = ["12 hour", "24 hour", "1 month", "3 month"]
        if timeframe not in valid_timeframes:
            bot.reply_to(message, f"Invalid timeframe. Use: {', '.join(valid_timeframes)}")
            return
        
        bot.reply_to(message, f"Capturing {symbol} liquidation heatmap ({timeframe})...")
        
        image_path = capture_coinglass_heatmap(symbol, timeframe)
        
        if image_path and os.path.exists(image_path):
            price = get_crypto_price(symbol)
            caption = f"{symbol} Liquidation Heatmap - {timeframe}"
            if price:
                caption += f"\n💰 {symbol} Price: {price}"
            
            with open(image_path, 'rb') as photo:
                bot.send_photo(message.chat.id, photo, caption=caption)
            os.remove(image_path)
        else:
            bot.reply_to(message, "Failed to capture heatmap. Please try again.")
            
    except Exception as e:
        logger.error(f"Error in map command: {e}")
        bot.reply_to(message, "An error occurred while processing your request.")

@bot.message_handler(commands=['start', 'help'])
def handle_help(message):
    """Handle help commands"""
    help_text = """
🔥 Liquidation Heatmap Bot

Commands:
/map <SYMBOL> [TIMEFRAME] - Get liquidation heatmap

Examples:
/map BTC
/map ETH 12 hour
/map BTC 24 hour
/map ETH 1 month

Supported timeframes: 12 hour, 24 hour, 1 month, 3 month
    """
    bot.reply_to(message, help_text)

if __name__ == "__main__":
    logger.info("Starting Liquidation Heatmap Bot...")
    bot.infinity_polling()

@bot.message_handler(commands=['map'])
def handle_map_command(message):
    """Handle /map command with symbol and timeframe"""
    try:
        parts = message.text.split()
        
        if len(parts) < 2:
            bot.reply_to(message, "Usage: /map <SYMBOL> [TIMEFRAME]\nExample: /map BTC 24 hour")
            return
        
        symbol = parts[1].upper()
        timeframe = " ".join(parts[2:]) if len(parts) > 2 else "24 hour"
        
        valid_timeframes = ["12 hour", "24 hour", "1 month", "3 month"]
        if timeframe not in valid_timeframes:
            bot.reply_to(message, f"Invalid timeframe. Use: {', '.join(valid_timeframes)}")
            return
        
        bot.reply_to(message, f"Capturing {symbol} liquidation heatmap ({timeframe})...")
        
        image_path = capture_coinglass_heatmap(symbol, timeframe)
        
        if image_path and os.path.exists(image_path):
            price = get_crypto_price(symbol)
            caption = f"{symbol} Liquidation Heatmap - {timeframe}"
            if price:
                caption += f"\n💰 {symbol} Price: {price}"
            
            with open(image_path, 'rb') as photo:
                bot.send_photo(message.chat.id, photo, caption=caption)
            os.remove(image_path)
        else:
            bot.reply_to(message, "Failed to capture heatmap. Please try again.")
            
    except Exception as e:
        logger.error(f"Error in map command: {e}")
        bot.reply_to(message, "An error occurred while processing your request.")

@bot.message_handler(commands=['start', 'help'])
def handle_help(message):
    """Handle help commands"""
    help_text = """
🔥 Liquidation Heatmap Bot

Commands:
/map <SYMBOL> [TIMEFRAME] - Get liquidation heatmap

Examples:
/map BTC
/map ETH 12 hour
/map BTC 24 hour
/map ETH 1 month

Supported timeframes: 12 hour, 24 hour, 1 month, 3 month
    """
    bot.reply_to(message, help_text)

if __name__ == "__main__":
    logger.info("Starting Liquidation Heatmap Bot...")
    bot.infinity_polling()