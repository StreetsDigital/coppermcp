"""Client for interacting with Copper's Opportunities API.

This module provides a client for managing opportunities in Copper CRM.
"""
from typing import List, Dict, Any, Optional

from ..models import Opportunity, OpportunityCreate, OpportunityUpdate, Activity, ActivityCreate
from .base import BaseEntityClient


class OpportunitiesClient(BaseEntityClient):
    """Client for managing opportunities in Copper CRM."""
    
    ENDPOINT = "opportunities"
    
    def list(self, page_size: int = 25, page_number: int = 1) -> List[Opportunity]:
        """List opportunities with pagination.
        
        Args:
            page_size: Number of records per page
            page_number: Page number to fetch
            
        Returns:
            List of opportunities
        """
        data = self.search({
            "page_size": page_size,
            "page_number": page_number,
            "sort_by": "name"
        })
        return [Opportunity.model_validate(item) for item in data]
    
    def get(self, opportunity_id: int) -> Opportunity:
        """Get an opportunity by ID.
        
        Args:
            opportunity_id: The ID of the opportunity to retrieve
            
        Returns:
            Opportunity data
        """
        data = self.base_client._get(f"{self.ENDPOINT}/{opportunity_id}")
        return Opportunity.model_validate(data)
    
    def create(self, data: OpportunityCreate) -> Opportunity:
        """Create a new opportunity.
        
        Args:
            data: Opportunity data including required fields
                
        Returns:
            Created opportunity data
        """
        response = self.base_client._post(self.ENDPOINT, json=data.model_dump(exclude_none=True))
        return Opportunity.model_validate(response)
    
    def update(self, opportunity_id: int, data: OpportunityUpdate) -> Opportunity:
        """Update an opportunity.
        
        Args:
            opportunity_id: The ID of the opportunity to update
            data: Opportunity data to update
            
        Returns:
            Updated opportunity data
        """
        response = self.base_client._put(
            f"{self.ENDPOINT}/{opportunity_id}",
            json=data.model_dump(exclude_none=True)
        )
        return Opportunity.model_validate(response)
    
    def delete(self, opportunity_id: int) -> Dict[str, Any]:
        """Delete an opportunity.
        
        Args:
            opportunity_id: The ID of the opportunity to delete
            
        Returns:
            Response data
        """
        return self.base_client._delete(f"{self.ENDPOINT}/{opportunity_id}")
    
    def get_related(self, opportunity_id: int, entity_type: str) -> List[Dict[str, Any]]:
        """Get entities related to an opportunity.
        
        Args:
            opportunity_id: The ID of the opportunity
            entity_type: Type of related entity (e.g., 'companies', 'people')
            
        Returns:
            List of related entities
        """
        return self.base_client._get(f"{self.ENDPOINT}/{opportunity_id}/related/{entity_type}")
    
    def update_custom_fields(self, opportunity_id: int, custom_fields: List[Dict[str, Any]]) -> Opportunity:
        """Update custom fields for an opportunity.
        
        Args:
            opportunity_id: The ID of the opportunity
            custom_fields: List of custom field updates
                Each field should have 'custom_field_definition_id' and 'value'
            
        Returns:
            Updated opportunity data
        """
        response = self.base_client._put(
            f"{self.ENDPOINT}/{opportunity_id}/custom_fields",
            json={'custom_fields': custom_fields}
        )
        return Opportunity.model_validate(response)
    
    def get_activities(self, opportunity_id: int) -> List[Activity]:
        """Get activities associated with an opportunity.
        
        Args:
            opportunity_id: The ID of the opportunity
            
        Returns:
            List of activities
        """
        data = self.base_client._post("activities/search", json={
            "parent": {
                "id": opportunity_id,
                "type": "opportunity"
            }
        })
        return [Activity.model_validate(item) for item in data]
    
    def add_activity(self, opportunity_id: int, activity_data: ActivityCreate) -> Activity:
        """Add an activity to an opportunity.
        
        Args:
            opportunity_id: The ID of the opportunity
            activity_data: Activity details
                
        Returns:
            Created activity data
        """
        # Ensure parent is set correctly
        activity_data.parent.id = opportunity_id
        activity_data.parent.type = "opportunity"
        
        response = self.base_client._post(
            'activities',
            json=activity_data.model_dump(exclude_none=True)
        )
        return Activity.model_validate(response)
    
    def get_pipelines(self) -> List[Dict[str, Any]]:
        """Get all available pipelines.
        
        Returns:
            List of pipelines with their stages
        """
        return self.base_client._get("pipelines")
    
    def get_pipeline(self, pipeline_id: int) -> Dict[str, Any]:
        """Get a specific pipeline.
        
        Args:
            pipeline_id: The ID of the pipeline to retrieve
            
        Returns:
            Pipeline data with stages
        """
        return self.base_client._get(f"pipelines/{pipeline_id}")
    
    def get_customer_sources(self) -> List[Dict[str, Any]]:
        """Get all available customer sources.
        
        Returns:
            List of customer sources
        """
        return self.base_client._get("customer_sources")
    
    def get_loss_reasons(self) -> List[Dict[str, Any]]:
        """Get all available loss reasons.
        
        Returns:
            List of loss reasons
        """
        return self.base_client._get("loss_reasons") 