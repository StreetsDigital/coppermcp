"""Run the FastAPI application with STDIO transport.

This script starts the FastAPI application using STDIO transport for MCP compatibility.
"""
import asyncio
import logging
from main import app
from transport.stdio import create_stdio_transport

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    """Start the STDIO transport."""
    logger.info("Starting Copper MCP Server with STDIO transport")
    transport = create_stdio_transport(app)
    await transport.run()

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main()) 