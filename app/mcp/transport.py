"""MCP transport base class."""

from abc import ABC, abstractmethod
from typing import Dict, Any, AsyncIterator

class BaseTransport(ABC):
    """Base class for MCP transports."""
    
    @abstractmethod
    async def run(self) -> None:
        """Run the transport."""
        pass
        
    @abstractmethod
    async def process_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Process a command and return a response.
        
        Args:
            command: The command to process
            
        Returns:
            The response from processing the command
        """
        pass
        
    @abstractmethod
    async def read_commands(self) -> AsyncIterator[Dict[str, Any]]:
        """Read commands from the transport.
        
        Yields:
            Commands to process
        """
        pass
        
    @abstractmethod
    async def write_response(self, response: Dict[str, Any]) -> None:
        """Write a response to the transport.
        
        Args:
            response: The response to write
        """
        pass 