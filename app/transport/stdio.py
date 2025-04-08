"""STDIO transport implementation."""
import json
import sys
import os
from typing import Dict, Any, TextIO, Optional
import logging
from fastapi import FastAPI
from fastapi.testclient import TestClient

from .base import Transport

# Set up logging
logger = logging.getLogger(__name__)

class STDIOTransport(Transport):
    """Transport that communicates via STDIO."""

    def __init__(self, app: FastAPI, stdin: TextIO = sys.stdin, stdout: TextIO = sys.stdout):
        """Initialize the transport.
        
        Args:
            app: FastAPI application instance
            stdin: Input stream (defaults to sys.stdin)
            stdout: Output stream (defaults to sys.stdout)
        """
        self.app = app
        self.client = TestClient(app)
        self.stdin = stdin
        self.stdout = stdout

    async def run(self) -> None:
        """Run the transport, reading commands from stdin."""
        while True:
            try:
                line = self.stdin.readline()
                if not line:
                    break
                    
                command = json.loads(line)
                response = await self.process_command(command)
                
                self.stdout.write(json.dumps(response) + "\n")
                self.stdout.flush()
                
            except json.JSONDecodeError:
                self._write_error("Invalid JSON")
            except Exception as e:
                logger.exception("Error processing command")
                self._write_error(str(e))

    async def process_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a command received via STDIO.
        
        Args:
            command: Dictionary containing:
                - api_token: Copper API token
                - user_email: Copper user email
                - method: HTTP method
                - path: API endpoint path
                - data: Optional request data
                
        Returns:
            Dictionary with response data or error
        """
        # Validate required fields
        required = ["api_token", "user_email", "method", "path"]
        missing = [f for f in required if f not in command]
        if missing:
            return {"error": f"Missing required fields: {', '.join(missing)}"}
            
        # Set environment variables for request
        os.environ["COPPER_API_TOKEN"] = command["api_token"]
        os.environ["COPPER_USER_EMAIL"] = command["user_email"]
        
        try:
            # Get request parameters
            method = command["method"].upper()
            path = command["path"]
            data = command.get("data")
            params = command.get("params", {})
            
            # Make request using test client
            if method == "GET":
                response = self.client.get(path, params=params)
            elif method == "POST":
                response = self.client.post(path, json=data)
            elif method == "PUT":
                response = self.client.put(path, json=data)
            elif method == "DELETE":
                response = self.client.delete(path)
            else:
                return {"error": f"Unsupported HTTP method: {method}"}
                
            # Return response
            return {
                "status": response.status_code,
                "data": response.json() if response.content else None
            }
            
        except Exception as e:
            logger.exception("Error processing request")
            return {"error": str(e)}
            
    def _write_error(self, message: str) -> None:
        """Write error response to stdout."""
        self.stdout.write(json.dumps({"error": message}) + "\n")
        self.stdout.flush()

def create_stdio_transport(app: FastAPI) -> STDIOTransport:
    """Create and return a new STDIO transport instance.
    
    Args:
        app: FastAPI application instance
        
    Returns:
        STDIOTransport: Configured transport instance
    """
    return STDIOTransport(app) 