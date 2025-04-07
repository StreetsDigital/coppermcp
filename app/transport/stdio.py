"""STDIO transport handler for FastAPI application.

This module provides STDIO transport support for the FastAPI application,
allowing it to communicate through standard input/output streams.
"""
import sys
import json
import asyncio
from typing import Dict, Any, Optional
from fastapi import FastAPI
from ..copper.auth import get_auth_token

class StdioTransport:
    """STDIO transport handler for FastAPI application."""
    
    def __init__(self, app: FastAPI):
        """Initialize STDIO transport.
        
        Args:
            app: FastAPI application instance
        """
        self.app = app
        self.loop = asyncio.get_event_loop()
    
    async def read_command(self) -> Dict[str, Any]:
        """Read a command from stdin.
        
        Returns:
            Dict[str, Any]: Parsed command data
        """
        try:
            line = await self.loop.run_in_executor(None, sys.stdin.readline)
            if not line:
                return None
            return json.loads(line)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON command"}
    
    async def write_response(self, response: Dict[str, Any]):
        """Write response to stdout.
        
        Args:
            response: Response data to write
        """
        try:
            output = json.dumps(response) + "\n"
            await self.loop.run_in_executor(None, sys.stdout.write, output)
            await self.loop.run_in_executor(None, sys.stdout.flush)
        except Exception as e:
            error_response = {
                "error": str(e),
                "status": 500
            }
            await self.loop.run_in_executor(None, sys.stdout.write, json.dumps(error_response) + "\n")
            await self.loop.run_in_executor(None, sys.stdout.flush)
    
    async def process_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Process a command through the FastAPI application.
        
        Args:
            command: Command data to process
            
        Returns:
            Dict[str, Any]: Response data
        """
        if not command or "path" not in command:
            return {
                "error": "Invalid command format. Must include 'path'.",
                "status": 400
            }
        
        # Convert command to ASGI scope
        scope = {
            "type": "http",
            "method": command.get("method", "GET"),
            "path": command["path"],
            "headers": [],
            "query_string": command.get("query", "").encode()
        }
        
        # Create receive channel
        async def receive():
            return {
                "type": "http.request",
                "body": json.dumps(command.get("body", {})).encode(),
                "more_body": False
            }
        
        # Create send channel
        response_body = []
        async def send(message):
            if message["type"] == "http.response.start":
                nonlocal response_status
                response_status = message["status"]
            elif message["type"] == "http.response.body":
                response_body.append(message["body"])
        
        response_status = None
        await self.app(scope, receive, send)
        
        # Combine response parts
        body = b"".join(response_body).decode()
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            pass
            
        return {
            "status": response_status,
            "body": body
        }
    
    async def start(self):
        """Start the STDIO transport handler."""
        while True:
            command = await self.read_command()
            if command is None:
                break
                
            response = await self.process_command(command)
            await self.write_response(response)

def create_stdio_transport(app: FastAPI) -> StdioTransport:
    """Create a STDIO transport handler for the FastAPI application.
    
    Args:
        app: FastAPI application instance
        
    Returns:
        StdioTransport: Configured transport handler
    """
    return StdioTransport(app) 