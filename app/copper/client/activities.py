"""Activities client for Copper CRM API.

This module provides the client class for interacting with activities in Copper CRM.
"""
from typing import Dict, Any, List, Optional
from .base import CopperClient

class ActivitiesClient:
    """Client for managing activities in Copper CRM."""
    
    def __init__(self, client: CopperClient):
        """Initialize the activities client.
        
        Args:
            client: The base Copper client
        """
        self.client = client
    
    async def list(
        self,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """List activities.
        
        Args:
            page_size: Number of records to return per page
            page_number: Page number to return
            
        Returns:
            List[Dict[str, Any]]: List of activities
        """
        params = {}
        if page_size is not None:
            params["page_size"] = page_size
        if page_number is not None:
            params["page_number"] = page_number
            
        return await self.client.get("/activities", params=params)
    
    async def get(self, activity_id: int) -> Dict[str, Any]:
        """Get an activity by ID.
        
        Args:
            activity_id: ID of the activity
            
        Returns:
            Dict[str, Any]: Activity details
        """
        return await self.client.get(f"/activities/{activity_id}")
    
    async def create(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new activity.
        
        Args:
            activity: Activity data
            
        Returns:
            Dict[str, Any]: Created activity
        """
        return await self.client.post("/activities", json=activity)
    
    async def update(self, activity_id: int, activity: Dict[str, Any]) -> Dict[str, Any]:
        """Update an activity.
        
        Args:
            activity_id: ID of the activity to update
            activity: Updated activity data
            
        Returns:
            Dict[str, Any]: Updated activity
        """
        return await self.client.put(f"/activities/{activity_id}", json=activity)
    
    async def delete(self, activity_id: int) -> None:
        """Delete an activity.
        
        Args:
            activity_id: ID of the activity to delete
        """
        await self.client.delete(f"/activities/{activity_id}")
    
    async def search(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for activities.
        
        Args:
            query: Search criteria
            
        Returns:
            List[Dict[str, Any]]: Matching activities
        """
        return await self.client.post("/activities/search", json=query) 