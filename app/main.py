"""
Main application entry point for the Copper CRM MCP server.

This module initializes and runs the MCP server with the appropriate transport
and error handling configuration.
"""

import os
import asyncio
from typing import Optional
from app.mcp_server import mcp
from app.transport.copper_transport import CopperMCPTransport
from app.errors import CopperAuthenticationError

async def main(transport_type: str = "stdio") -> None:
    """Initialize and run the MCP server.
    
    Args:
        transport_type: Type of transport to use ("stdio" or "http")
        
    Raises:
        CopperAuthenticationError: If required credentials are missing
    """
    # Get credentials from environment
    api_token = os.getenv("COPPER_API_TOKEN")
    email = os.getenv("COPPER_EMAIL")
    
    if not api_token or not email:
        raise CopperAuthenticationError(
            "Missing required credentials. Please set COPPER_API_TOKEN and COPPER_EMAIL environment variables."
        )
    
    # Initialize transport
    transport = CopperMCPTransport(api_token=api_token, email=email)
    
    # Run server with configured transport
    mcp.run(transport=transport)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down MCP server...")
    except Exception as e:
        print(f"Error running MCP server: {str(e)}")
        exit(1) 