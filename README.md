# Ultra-Lightweight MCP Server
[![smithery badge](https://smithery.ai/badge/@kdkiss/ultra-lightweight-mcp)](https://smithery.ai/server/@kdkiss/ultra-lightweight-mcp)

An ultra-lightweight MCP (Model Context Protocol) server designed for Smithery deployment with Playwright browser automation capabilities. This server provides fast startup (<5 seconds) and minimal resource usage while offering comprehensive browser automation tools.

## Features

- **Ultra-lightweight**: Minimal dependencies, fast startup
- **Smithery compatible**: Stdio transport with proper configuration
- **Browser automation**: Full Playwright integration
- **TypeScript**: Clean, type-safe implementation
- **Health checks**: Built-in monitoring capabilities
- **Graceful shutdown**: Proper resource cleanup

## Tools Available

1. **navigate_to_url** - Navigate to any URL and return page information
2. **take_screenshot** - Capture screenshots of pages or specific elements
3. **click_element** - Click elements on the page
4. **fill_form** - Fill form fields with specified values
5. **extract_text** - Extract text content from pages

## Quick Start

### Installing via Smithery

To install Ultra-Lightweight MCP Server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@kdkiss/ultra-lightweight-mcp):

```bash
npx -y @smithery/cli install @kdkiss/ultra-lightweight-mcp --client claude
```

### Smithery Deployment

The server is ready for Smithery deployment with the provided `smithery.yaml` configuration.

### Local Development

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Build the server**:
   ```bash
   npm run build
   ```

3. **Start the server**:
   ```bash
   npm start
   ```

4. **Development mode** (with hot reload):
   ```bash
   npm run dev
   ```

### Docker Usage

```bash
# Build the image
docker build -t ultra-lightweight-mcp .

# Run the container
docker run -i ultra-lightweight-mcp
```

## Configuration

### Environment Variables

- `NODE_ENV`: Set to 'production' for production deployments
- `DEBUG`: Enable debug logging when needed

### Smithery Configuration

The `smithery.yaml` file contains all necessary configuration for Smithery deployment including:
- Resource limits (512Mi memory, 500m CPU)
- Health check endpoints
- Logging configuration
- Environment setup

## Usage Examples

### Navigate to a URL
```json
{
  "tool": "navigate_to_url",
  "arguments": {
    "url": "https://example.com",
    "waitFor": "body"
  }
}
```

### Take a Screenshot
```json
{
  "tool": "take_screenshot",
  "arguments": {
    "fullPage": true
  }
}
```

### Click an Element
```json
{
  "tool": "click_element",
  "arguments": {
    "selector": "button[type='submit']"
  }
}
```

### Fill a Form
```json
{
  "tool": "fill_form",
  "arguments": {
    "selector": "input[name='email']",
    "value": "user@example.com"
  }
}
```

### Extract Text
```json
{
  "tool": "extract_text",
  "arguments": {
    "selector": ".content"
  }
}
```

## Performance

- **Startup time**: <5 seconds
- **Memory usage**: <512Mi
- **CPU usage**: <500m
- **Dependencies**: Only 2 (MCP SDK + Playwright)

## Development

### Project Structure
```
ultra-lightweight-mcp-server/
├── src/
│   └── index.ts          # Main server implementation
├── dist/                 # Compiled JavaScript
├── package.json          # Dependencies and scripts
├── tsconfig.json         # TypeScript configuration
├── smithery.yaml         # Smithery deployment config
└── README.md            # This file
```

### Building from Source

1. Clone or create the project structure
2. Install dependencies: `npm install`
3. Build: `npm run build`
4. Test: `npm start`

### Testing

The server can be tested using any MCP client or directly via stdio. For testing:

```bash
# Start the server
npm start

# In another terminal, test with curl or MCP client
echo '{"type":"list_tools"}' | node dist/index.js
```

## Troubleshooting

### Common Issues

1. **Browser not starting**: Ensure Playwright dependencies are installed
2. **Memory issues**: Check resource limits in smithery.yaml
3. **Timeout errors**: Increase wait timeouts in tool calls
4. **Permission errors**: Ensure proper file permissions

### Debug Mode

Enable debug logging:
```bash
DEBUG=* npm start
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please open an issue on the repository or contact the maintainers.
