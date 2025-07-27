# Liquidation Heatmap Bot

A Telegram bot that captures cryptocurrency liquidation heatmaps from Coinglass and delivers them on demand with real-time price information.

## Features

- 📊 **Real-time Heatmaps**: Captures liquidation heatmaps for any supported cryptocurrency
- 💰 **Price Integration**: Shows current cryptocurrency prices alongside heatmaps
- ⏰ **Multiple Timeframes**: Supports 12 hour, 24 hour, 1 month, and 3 month views
- 🤖 **Easy Commands**: Simple Telegram commands for instant access
- 🔄 **Automated Symbol Selection**: Dynamically switches between different cryptocurrencies

## Supported Cryptocurrencies

- Bitcoin (BTC)
- Ethereum (ETH)
- Binance Coin (BNB)
- Cardano (ADA)
- Solana (SOL)
- Ripple (XRP)
- Polkadot (DOT)
- Dogecoin (DOGE)
- Avalanche (AVAX)
- Polygon (MATIC)

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/map <SYMBOL> [TIMEFRAME]` | Get liquidation heatmap | `/map ETH 12 hour` |
| `/start` or `/help` | Show help information | `/help` |

### Supported Timeframes
- `12 hour`
- `24 hour` (default)
- `1 month`
- `3 month`

## Setup

### Prerequisites

- Docker and Docker Compose
- Telegram Bot Token
- Telegram Channel ID (optional)

### Environment Variables

Create a `.env` file in the project root:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=your_channel_id_here
SELENIUM_HOST=selenium
SELENIUM_PORT=4444
```

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd liquidation_map_bot
```

2. Create the `.env` file with your configuration

3. Start the services:
```bash
docker-compose up -d
```

**Note**: If you're using an ARM-based device (Apple Silicon Mac, Raspberry Pi, etc.), make sure to use the ARM-specific docker-compose.yml configuration shown above with `seleniarm/standalone-chromium:latest` instead of the standard selenium image.

## Docker Configuration

The project uses Docker Compose with two services:

- **selenium**: Headless Chrome browser for web scraping
- **bot**: Python application running the Telegram bot

### docker-compose.yml

**For x86/x64 systems:**
```yaml
version: '3.8'
services:
  selenium:
    image: selenium/standalone-chrome:latest
    ports:
      - "4444:4444"
      - "7900:7900"
    environment:
      - SE_NODE_SESSION_TIMEOUT=300
      - SE_NODE_MAX_SESSIONS=1
    volumes:
      - /dev/shm:/dev/shm

  bot:
    build: .
    depends_on:
      - selenium
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
```

**For ARM devices (Apple Silicon, Raspberry Pi, etc.):**
```yaml
version: '3.8'
services:
  selenium:
    image: seleniarm/standalone-chromium:latest
    shm_size: 2gb
    ports:
      - "4444:4444"
    restart: always

  bot:
    build: .
    depends_on:
      - selenium
    env_file:
      - .env
    environment:
      - SELENIUM_HOST=selenium
      - SELENIUM_PORT=4444
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
```

## Usage Examples

```
/map BTC                    # BTC heatmap (24 hour default)
/map ETH 12 hour           # ETH heatmap for 12 hours
/map BTC 1 month           # BTC heatmap for 1 month
/map DOGE 3 month          # DOGE heatmap for 3 months
```

## Technical Details

### Architecture
- **Web Scraping**: Selenium WebDriver with Chrome headless
- **Image Processing**: PIL for screenshot optimization
- **API Integration**: CoinGecko API for real-time prices
- **Bot Framework**: pyTelegramBotAPI

### Key Components
- `capture_coinglass_heatmap()`: Main scraping function with symbol selection
- `get_crypto_price()`: Fetches current cryptocurrency prices
- `handle_map_command()`: Processes Telegram commands
- Automated symbol switching using ActionChains for realistic user simulation

### Screenshot Process
1. Navigate to Coinglass liquidation heatmap page
2. Select Symbol tab and input desired cryptocurrency
3. Set timeframe via dropdown selection
4. Capture chart area using Chrome DevTools Protocol
5. Process and optimize image for Telegram delivery

## Logging

Logs are stored in `./logs/bot.log` and include:
- Connection status to Selenium
- Symbol selection attempts
- Screenshot capture results
- Error handling and debugging information

## Troubleshooting

### Common Issues

**Bot not responding**: Check if Selenium container is running
```bash
docker-compose logs selenium
```

**Symbol selection fails**: Verify the website structure hasn't changed
```bash
docker-compose logs bot
```

**Image quality issues**: Adjust window size in `setup_webdriver()` function

### Debug Mode

Enable debug logging by modifying the logging level in `bot.py`:
```python
logging.basicConfig(level=logging.DEBUG, ...)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with different cryptocurrencies and timeframes
5. Submit a pull request

## License

This project is for educational purposes. Please respect Coinglass's terms of service and rate limits.

## Disclaimer

This bot is for informational purposes only. Cryptocurrency trading involves substantial risk. Always do your own research before making investment decisions.