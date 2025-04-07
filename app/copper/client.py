"""Main client for the Copper API.

This module provides the main client class for interacting with the Copper API.
"""

import os
from typing import Optional

from .base import CopperBaseClient
from .entities import (
    ActivitiesClient,
    CompaniesClient,
    OpportunitiesClient,
    PeopleClient,
    TasksClient,
)


class CopperClient:
    """Main client for interacting with the Copper API."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        email: Optional[str] = None,
        base_url: str = "https://api.copper.com/developer_api/v1"
    ):
        """Initialize the Copper client.
        
        Args:
            api_key: Copper API key. If not provided, will look for COPPER_API_KEY env var
            email: Copper user email. If not provided, will look for COPPER_USER_EMAIL env var
            base_url: Base URL for the Copper API
        """
        self.api_key = api_key or os.getenv("COPPER_API_KEY")
        self.email = email or os.getenv("COPPER_USER_EMAIL")
        
        if not self.api_key:
            raise ValueError("API key must be provided or set in COPPER_API_KEY env var")
        if not self.email:
            raise ValueError("Email must be provided or set in COPPER_USER_EMAIL env var")
            
        self.base_client = CopperBaseClient(
            api_key=self.api_key,
            email=self.email,
            base_url=base_url
        )
        
        # Initialize entity clients
        self.activities = ActivitiesClient(self.base_client)
        self.companies = CompaniesClient(self.base_client)
        self.opportunities = OpportunitiesClient(self.base_client)
        self.people = PeopleClient(self.base_client)
        self.tasks = TasksClient(self.base_client) 