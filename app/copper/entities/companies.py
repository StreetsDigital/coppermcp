"""Client for interacting with Copper's Companies API.

This module provides a client for managing companies in Copper CRM.
"""
from typing import List, Dict, Any, Optional

from ..models import Company, CompanyCreate, CompanyUpdate, Activity, ActivityCreate
from .base import BaseEntityClient


class CompaniesClient(BaseEntityClient):
    """Client for managing companies in Copper CRM."""
    
    ENDPOINT = "companies"
    
    def list(self, page_size: int = 25, page_number: int = 1) -> List[Company]:
        """List companies with pagination.
        
        Args:
            page_size: Number of records per page
            page_number: Page number to fetch
            
        Returns:
            List of companies
        """
        data = self.search({
            "page_size": page_size,
            "page_number": page_number,
            "sort_by": "name"
        })
        return [Company.model_validate(item) for item in data]
    
    def get(self, company_id: int) -> Company:
        """Get a company by ID.
        
        Args:
            company_id: The ID of the company to retrieve
            
        Returns:
            Company data
        """
        data = self.base_client._get(f"{self.ENDPOINT}/{company_id}")
        return Company.model_validate(data)
    
    def create(self, data: CompanyCreate) -> Company:
        """Create a new company.
        
        Args:
            data: Company data including required fields
                
        Returns:
            Created company data
        """
        response = self.base_client._post(self.ENDPOINT, json=data.model_dump(exclude_none=True))
        return Company.model_validate(response)
    
    def update(self, company_id: int, data: CompanyUpdate) -> Company:
        """Update a company.
        
        Args:
            company_id: The ID of the company to update
            data: Company data to update
            
        Returns:
            Updated company data
        """
        response = self.base_client._put(
            f"{self.ENDPOINT}/{company_id}",
            json=data.model_dump(exclude_none=True)
        )
        return Company.model_validate(response)
    
    def delete(self, company_id: int) -> Dict[str, Any]:
        """Delete a company.
        
        Args:
            company_id: The ID of the company to delete
            
        Returns:
            Response data
        """
        return self.base_client._delete(f"{self.ENDPOINT}/{company_id}")
    
    def get_related(self, company_id: int, entity_type: str) -> List[Dict[str, Any]]:
        """Get entities related to a company.
        
        Args:
            company_id: The ID of the company
            entity_type: Type of related entity (e.g., 'opportunities', 'people')
            
        Returns:
            List of related entities
        """
        return self.base_client._get(f"{self.ENDPOINT}/{company_id}/related/{entity_type}")
    
    def update_custom_fields(self, company_id: int, custom_fields: List[Dict[str, Any]]) -> Company:
        """Update custom fields for a company.
        
        Args:
            company_id: The ID of the company
            custom_fields: List of custom field updates
                Each field should have 'custom_field_definition_id' and 'value'
            
        Returns:
            Updated company data
        """
        response = self.base_client._put(
            f"{self.ENDPOINT}/{company_id}/custom_fields",
            json={'custom_fields': custom_fields}
        )
        return Company.model_validate(response)
    
    def get_activities(self, company_id: int) -> List[Activity]:
        """Get activities associated with a company.
        
        Args:
            company_id: The ID of the company
            
        Returns:
            List of activities
        """
        data = self.base_client._post("activities/search", json={
            "parent": {
                "id": company_id,
                "type": "company"
            }
        })
        return [Activity.model_validate(item) for item in data]
    
    def add_activity(self, company_id: int, activity_data: ActivityCreate) -> Activity:
        """Add an activity to a company.
        
        Args:
            company_id: The ID of the company
            activity_data: Activity details
                
        Returns:
            Created activity data
        """
        # Ensure parent is set correctly
        activity_data.parent.id = company_id
        activity_data.parent.type = "company"
        
        response = self.base_client._post(
            'activities',
            json=activity_data.model_dump(exclude_none=True)
        )
        return Activity.model_validate(response) 