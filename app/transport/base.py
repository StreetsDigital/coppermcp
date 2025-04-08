"""Base transport class for FastAPI application."""
from abc import ABC, abstractmethod
from typing import Dict, Any

class Transport(ABC):
    """Abstract base class for transports."""
    
    @abstractmethod
    async def run(self) -> None:
        """Run the transport."""
        pass
        
    @abstractmethod
    async def process_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a command received via the transport.
        
        Args:
            command: Dictionary containing command data
            
        Returns:
            Dictionary with response data or error
        """
        pass 