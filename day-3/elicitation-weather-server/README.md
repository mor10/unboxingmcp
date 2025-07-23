# Elicitation Demo: Weather MCP Server Powered by the Open-Meteo API

This MCP server interfaces with the [Open-Meteo Geocoding API](https://open-meteo.com/en/docs/geocoding-api) to transform a location name to a latitude and longitude, and then uses the [Open-Meteo Weather API](https://open-meteo.com/en/docs/weather-api) to fetch current weather conditions and forecasts for that location.

When the geocoding API returns more than one result for a location, it uses [Elicitations](https://modelcontextprotocol.io/specification/draft/client/elicitation) to surface the options to the user and ask them to pick a location before proceeding to the weather API.

## Requirements

- [uv](https://docs.astral.sh/uv/):
   - macOS via Homebrew:
   ```bash
   brew install uv
   ```
   - Windows via WinGet:
   ```bash
   winget install --id=astral-sh.uv  -e
   ```
- [Visual Studio Code Insiders](https://code.visualstudio.com/insiders/) for elicitations support

## Development

### 1. Set up the uv environment

In terminal:
```bash
uv sync
```
### 2. Start the virtual environment

In terminal:
```bash
source .venv/bin/activate
```

NOTE: To stop the virtual environment:
```bash
deactivate
```

### 3. Set the VS Code python environment

1. Open the Command Palette Shift + CMD/CTRL + P
2. Select "Python: Set Project Environment
3. Choose `mcp-open-meteo-elicit` venv

### 4. Run MCP server in dev mode with the [MCP Inspector](https://github.com/modelcontextprotocol/inspector)

```bash
uv run mcp dev mcp_open_meteo_elicit/server.py
```

## Run MCP server in VS Code

1. Open the Command Palette Shift + CMD/CTRL + P

2. Select "MCP: Open User Configuration". This opens `mcp.json`

3. In `mcp.json`:

  ```json
  {
    "servers": {
      "weather-server": {
        "type": "stdio",
        "command": "uv",
        "args": [
          "run",
          "--directory",
          "/absolute/path/to/elicitation-weather-server",
          "mcp-open-meteo-elicit"
        ]
      }
    },
    "inputs": []
  }
  ```

## Run MCP server in Claude Desktop

NOTE: As of July 23, 2025, Claude Desktop does not support elicitations. Once support is added, the following steps will allow you to run the MCP server in Claude Desktop.

### Automatic install

In terminal:
```bash
uv run mcp install mcp_open_meteo_elicit/server.py
```

### Manual install

1. Open `claude_desktop_config.js` in an editor:
 
  File location:
  - MacOS / Linux `~/Library/Application/Support/Claude/claude_desktop_config.json`
  - Windows `AppData\Claude\claude_desktop_config.json`

2. Find the full path to `uv`:
  
  - MacOS / Linux:
  ```bash
  which uv
  ```
  - Windows:
  ```bash
  where uv
  ```

2. In `claude_desktop_config.js`

  ```json
  {
    "mcpServers": {
      "Open-Meteo Weather": {
        "command": "/opt/homebrew/bin/uv",
        "args": [
          "run",
          "--with",
          "mcp[cli]",
          "mcp",
          "run",
          "/absolute/path/to/elicitation-weather-server/mcp_open_meteo_elicit/server.py"
        ]
      }
    }
   }
   ```

