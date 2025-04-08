"""Base entity client for the Copper API.

This module provides the base entity client class that all entity clients inherit from.
"""
from typing import Any, Dict, List, Optional

from ..base import CopperBaseClient


class BaseEntityClient:
    """Base client for entity-specific operations."""
    
    ENDPOINT: str = ""  # Override in subclasses
    
    def __init__(self, base_client: CopperBaseClient):
        """Initialize the entity client.
        
        Args:
            base_client: Base client for making HTTP requests
        """
        self.base_client = base_client
    
    def list(self, page_size: int = 25, page_number: int = 1) -> List[Dict[str, Any]]:
        """List entities with pagination.
        
        Args:
            page_size: Number of records per page
            page_number: Page number to fetch
            
        Returns:
            List of entities
        """
        params = {
            'page_size': page_size,
            'page': page_number
        }
        return self.base_client.get(self.ENDPOINT, params=params)
    
    def get(self, entity_id: int) -> Dict[str, Any]:
        """Get a single entity by ID.
        
        Args:
            entity_id: The ID of the entity to retrieve
            
        Returns:
            Entity data
        """
        return self.base_client.get(f"{self.ENDPOINT}/{entity_id}")
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new entity.
        
        Args:
            data: Entity data to create
            
        Returns:
            Created entity data
        """
        return self.base_client.post(self.ENDPOINT, json=data)
    
    def update(self, entity_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing entity.
        
        Args:
            entity_id: The ID of the entity to update
            data: Updated entity data
            
        Returns:
            Updated entity data
        """
        return self.base_client.put(f"{self.ENDPOINT}/{entity_id}", json=data)
    
    def delete(self, entity_id: int) -> Dict[str, Any]:
        """Delete an entity.
        
        Args:
            entity_id: The ID of the entity to delete
            
        Returns:
            Response data
        """
        return self.base_client.delete(f"{self.ENDPOINT}/{entity_id}")
    
    def search(
        self,
        query: Optional[Dict[str, Any]] = None,
        page_size: int = 25,
        page_number: int = 1
    ) -> List[Dict[str, Any]]:
        """Search for entities with pagination.
        
        Args:
            query: Search query parameters
            page_size: Number of records per page
            page_number: Page number to fetch
            
        Returns:
            List of matching entities
        """
        data = query or {}
        data.update({
            "page_size": page_size,
            "page_number": page_number
        })
        
        return self.base_client.post(f"{self.ENDPOINT}/search", json=data) 