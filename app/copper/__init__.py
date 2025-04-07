"""Copper CRM API client package.

This package provides a client for interacting with the Copper CRM API.
"""
from typing import Optional

from .client_base import CopperBaseClient
from .entities.people import PeopleClient


class CopperClient:
    """Main client class that provides access to all Copper API functionality."""
    
    def __init__(self, base_client: Optional[CopperBaseClient] = None):
        """Initialize the Copper client.
        
        Args:
            base_client: Optional pre-configured base client
        """
        self._base_client = base_client or CopperBaseClient()
        
        # Initialize entity clients
        self.people = PeopleClient(self._base_client)


def create_copper_client() -> CopperClient:
    """Create a new instance of the Copper client.
    
    Returns:
        Configured CopperClient instance
    """
    return CopperClient()


# For convenience, create a default client instance
default_client = create_copper_client()
