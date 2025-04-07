"""Client for interacting with Copper's People API.

This module provides a client for managing people (contacts) in Copper CRM.
"""
from typing import List, Dict, Any, Optional

from ..models import Person, PersonCreate, PersonUpdate, Activity, ActivityCreate
from .base import BaseEntityClient


class PeopleClient(BaseEntityClient):
    """Client for managing people in Copper CRM."""
    
    ENDPOINT = "people"
    
    def list(self, page_size: int = 25, page_number: int = 1) -> List[Person]:
        """List people with pagination.
        
        Args:
            page_size: Number of records per page
            page_number: Page number to fetch
            
        Returns:
            List of people
        """
        data = self.search({
            "page_size": page_size,
            "page_number": page_number,
            "sort_by": "name"
        })
        return [Person.model_validate(item) for item in data]
    
    def get(self, person_id: int) -> Person:
        """Get a person by ID.
        
        Args:
            person_id: The ID of the person to retrieve
            
        Returns:
            Person data
        """
        data = self.base_client._get(f"{self.ENDPOINT}/{person_id}")
        return Person.model_validate(data)
    
    def create(self, data: PersonCreate) -> Person:
        """Create a new person.
        
        Args:
            data: Person data including required fields
                
        Returns:
            Created person data
        """
        response = self.base_client._post(self.ENDPOINT, json=data.model_dump(exclude_none=True))
        return Person.model_validate(response)
    
    def update(self, person_id: int, data: PersonUpdate) -> Person:
        """Update a person.
        
        Args:
            person_id: The ID of the person to update
            data: Person data to update
            
        Returns:
            Updated person data
        """
        response = self.base_client._put(
            f"{self.ENDPOINT}/{person_id}",
            json=data.model_dump(exclude_none=True)
        )
        return Person.model_validate(response)
    
    def delete(self, person_id: int) -> Dict[str, Any]:
        """Delete a person.
        
        Args:
            person_id: The ID of the person to delete
            
        Returns:
            Response data
        """
        return self.base_client._delete(f"{self.ENDPOINT}/{person_id}")
    
    def get_related(self, person_id: int, entity_type: str) -> List[Dict[str, Any]]:
        """Get entities related to a person.
        
        Args:
            person_id: The ID of the person
            entity_type: Type of related entity (e.g., 'opportunities', 'tasks')
            
        Returns:
            List of related entities
        """
        return self.base_client._get(f"{self.ENDPOINT}/{person_id}/related/{entity_type}")
    
    def update_custom_fields(self, person_id: int, custom_fields: List[Dict[str, Any]]) -> Person:
        """Update custom fields for a person.
        
        Args:
            person_id: The ID of the person
            custom_fields: List of custom field updates
                Each field should have 'custom_field_definition_id' and 'value'
            
        Returns:
            Updated person data
        """
        response = self.base_client._put(
            f"{self.ENDPOINT}/{person_id}/custom_fields",
            json={'custom_fields': custom_fields}
        )
        return Person.model_validate(response)
    
    def convert_lead(self, person_id: int, details: Optional[Dict[str, Any]] = None) -> Person:
        """Convert a lead to a person.
        
        Args:
            person_id: The ID of the lead to convert
            details: Optional conversion details
            
        Returns:
            Converted person data
        """
        response = self.base_client._post(
            f"{self.ENDPOINT}/{person_id}/convert",
            json=details or {}
        )
        return Person.model_validate(response)
    
    def get_activities(self, person_id: int) -> List[Activity]:
        """Get activities associated with a person.
        
        Args:
            person_id: The ID of the person
            
        Returns:
            List of activities
        """
        data = self.base_client._post("activities/search", json={
            "parent": {
                "id": person_id,
                "type": "person"
            }
        })
        return [Activity.model_validate(item) for item in data]
    
    def add_activity(self, person_id: int, activity_data: ActivityCreate) -> Activity:
        """Add an activity to a person.
        
        Args:
            person_id: The ID of the person
            activity_data: Activity details
                
        Returns:
            Created activity data
        """
        # Ensure parent is set correctly
        activity_data.parent.id = person_id
        activity_data.parent.type = "person"
        
        response = self.base_client._post(
            'activities',
            json=activity_data.model_dump(exclude_none=True)
        )
        return Activity.model_validate(response) 