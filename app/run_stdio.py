"""Run the FastAPI application with STDIO transport.

This script starts the FastAPI application using STDIO transport for MCP compatibility.
"""
import asyncio
import os
from dotenv import load_dotenv
from .main import app
from .transport.stdio import create_stdio_transport

async def main():
    """Main entry point for STDIO transport."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Create and start STDIO transport
    transport = create_stdio_transport(app)
    await transport.start()

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main()) 