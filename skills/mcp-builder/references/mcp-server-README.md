# fastapitemplate MCP Server

A Model Context Protocol (MCP) server that exposes the fastapitemplate's tools to AI clients like Claude Desktop, VS Code, and other MCP-compatible applications.

## Features

This MCP server provides comprehensive fastapitemplate's capabilities:

TODO: Add fastapitemplate's tools here

## Installation

1. **Install Python dependencies:**
   ```bash
   cd fastapitemplate/mcp-server
   pip install -r requirements.txt
   ```

2. **Run the server:**
   ```bash
   python mcp_server.py
   ```

## MCP Client Configuration

### Claude Desktop

Add this configuration to your `claude_desktop_config.json`:

For a local STDIO connection:

```json
{
  "mcpServers": {
    "fastapitemplate": {
      "command": "sh",
      "args": [
        "/absolute/path/to/fastapitemplate/mcp-server/run_mcp_server.sh"
      ],
      "env": {
        "GS_USER_ID": "xxxx",
        "GS_API_KEY": "xxxx"
      }
    }
  }
}
```

For a remote HTTP connection:

```json
{
  "mcpServers": {
    "fastapitemplate": {
      "url": "http://localhost:8070/mcp",
      "headers": {
        "Authorization": "Bearer sk-gsu-..."
      }
    }
  }
}
```

### VS Code MCP Extension

Add to your VS Code settings or `.vscode/mcp.json`:

For a local STDIO connection:

```json
{
  "mcp": {
    "servers": {
      "fastapitemplate": {
        "command": "sh",
        "args": [
          "/absolute/path/to/fastapitemplate/mcp-server/run_mcp_server.sh"
        ],
        "env": {
          "GS_USER_ID": "xxxx",
          "GS_API_KEY": "xxxx"
        }
      }
    }
  }
}
```

For a remote HTTP connection:

```json
{
  "mcp": {
    "servers": {
      "fastapitemplate": {
        "url": "http://localhost:8070/mcp",
        "headers": {
          "Authorization": "Bearer sk-gsu-..."
        }
      }
    }
  }
}
```

## Usage Examples

Once connected to an MCP client, you can interact with the server using natural language:

### Basic Operations
- TODO: Add fastapitemplate's tools here

## Architecture

The server is built using:
- **FastMCP**: Modern Python MCP framework for rapid development
- **Pydantic**: Data validation and serialization
- **AsyncIO**: Asynchronous operations for better performance

### Data Models
- TODO: Add fastapitemplate's data models here

### Mock Data
The server includes sample data for testing and demonstration:
- TODO: Add fastapitemplate's sample data here

## Development

### Extending the Server
To add new tools, create functions decorated with `@mcp.tool()`:

```python
@mcp.tool()
async def my_new_tool(params: MyModel) -> Dict[str, Any]:
    """Description of what this tool does"""
    # Implementation
    return {"success": True, "data": result}
```

### Adding Resources
To add new resources, use the `@mcp.resource()` decorator:

```python
@mcp.resource("mydata://endpoint")
async def my_resource() -> str:
    """Get my data as a resource"""
    data = await get_my_data()
    return json.dumps(data, indent=2)
```

## Integration with fastapitemplate

This MCP server is based on the fastapitemplate's AI tools:
- `ai_gpt_fn_app.py`: Core fastapitemplate tools

It provides the same functionality but exposed through the standardized MCP protocol, making it accessible to any MCP-compatible AI client.

## Transport Modes

Currently supports:
- **HTTP**: HTTP/SSE transport for remote clients (default)
- **STDIO**: Standard input/output for local clients

## Logging

The server provides detailed logging for debugging and monitoring:
- Tool invocations and parameters
- Data validation errors
- Mock database operations
- Performance metrics

## License

This MCP server follows the same license as the fastapitemplate project.