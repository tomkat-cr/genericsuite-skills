#!/usr/bin/env python3
"""
MCP Server
A Model Context Protocol server that exposes fastapitemplate's
tools to AI clients.
"""
from typing import Dict, Any
import os

from genericsuite.util.app_logger import log_info
from genericsuite.mcplib.util.create_app import create_app
from genericsuite.mcplib.util.utilities import (
    mcp_authenticate,
    verify_app_context,
    tool_result,
    get_access_token,
    # resource_result,
)

from lib.config.config import Config
from lib.models.ai_chatbot.ai_gpt_fn_app import (
    cac as cac_gpt_tools,
)

DEBUG = False

# Initialize FastMCP server
settings = Config()
app = create_app(app_name=f'{settings.APP_NAME.lower()}-mcp-server',
                 settings=settings, log_file='./logs/mcp_server.log')
mcp = app.mcp
cac_object_list = [cac_gpt_tools]


# ============================================================================
# MCP TOOLS - USER AUTHENTICATION
# ============================================================================


@mcp.tool()
async def get_api_keys() -> Dict[str, Any]:
    """
    Get API keys
    """
    _ = DEBUG and log_info("Getting API keys")
    result = {
        "resultset": {
            "access_token": get_access_token(),
            "GS_USER_ID": os.environ.get("GS_USER_ID"),
            "GS_USER_NAME": os.environ.get("GS_USER_NAME"),
            "GS_API_KEY": os.environ.get("GS_API_KEY")
        }
    }
    return result


@mcp.tool()
async def authentication_tool(
    username: str,
    password: str,
) -> str:
    """
    Authenticate user
    """
    _ = DEBUG and log_info("Authenticating user")
    if not username and not password:
        if verify_app_context(app, cac_object_list):
            return tool_result("User already authenticated with API key")
        else:
            return tool_result("Username and password are required")
    return mcp_authenticate(app, cac_object_list, username, password)


# ============================================================================
# MCP TOOLS
# ============================================================================


# ============================================================================
# MCP RESOURCES - DATA ACCESS
# ============================================================================


@mcp.resource("user://login/{username}/{password}",
              mime_type="application/json")
async def authenticate(
    username: str,
    password: str,
) -> str:
    """
    Get user login as a resource
    """
    _ = DEBUG and log_info("Getting user login for resource")
    return mcp_authenticate(app, cac_object_list, username, password)


# ============================================================================
# SERVER STARTUP AND CONFIGURATION
# ============================================================================


def main():
    """
    Main entry point for the MCP Server
    """
    print(f"🥗 Starting {settings.APP_NAME} MCP Server...")
    app.run()


if __name__ == "__main__":
    main()
