"""Client for managing Activities in Copper API."""
from typing import Optional, List, Dict, Any, Union

from ..base import CopperBaseClient
from ..models import Activity, ActivityCreate, ActivityUpdate


class ActivitiesClient:
    """Client for managing Activities in Copper API."""

    ENDPOINT = "activities"

    def __init__(self, base_client: CopperBaseClient):
        """Initialize the Activities client.
        
        Args:
            base_client: The base Copper client for making HTTP requests
        """
        self.base_client = base_client

    def get(self, activity_id: int) -> Activity:
        """Fetch an activity by ID.
        
        Args:
            activity_id: The ID of the activity to fetch
            
        Returns:
            Activity: The requested activity
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self.base_client._get(f"{self.ENDPOINT}/{activity_id}")
        return Activity.model_validate(response)

    def create(self, data: ActivityCreate) -> Activity:
        """Create a new activity.
        
        Args:
            data: The activity data
            
        Returns:
            Activity: The created activity
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self.base_client._post(self.ENDPOINT, json=data.model_dump(exclude_none=True))
        return Activity.model_validate(response)

    def update(self, activity_id: int, data: ActivityUpdate) -> Activity:
        """Update an existing activity.
        
        Args:
            activity_id: The ID of the activity to update
            data: The activity data to update
            
        Returns:
            Activity: The updated activity
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self.base_client._put(
            f"{self.ENDPOINT}/{activity_id}",
            json=data.model_dump(exclude_none=True)
        )
        return Activity.model_validate(response)

    def delete(self, activity_id: int) -> None:
        """Delete an activity.
        
        Args:
            activity_id: The ID of the activity to delete
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        self.base_client._delete(f"{self.ENDPOINT}/{activity_id}")

    def list(
        self,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_direction: Optional[str] = None,
        filter_by: Optional[Dict[str, Any]] = None
    ) -> List[Activity]:
        """List activities with optional filtering and pagination.
        
        Args:
            page_size: Number of records to return per page
            page_number: Page number to return
            sort_by: Field to sort by
            sort_direction: Sort direction ('asc' or 'desc')
            filter_by: Dictionary of fields to filter by
            
        Returns:
            List[Activity]: List of activities matching the criteria
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        params = {
            "page_size": page_size,
            "page": page_number,
            "sort_by": sort_by,
            "sort_direction": sort_direction,
            **(filter_by or {})
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        response = self.base_client._post(f"{self.ENDPOINT}/search", json=params)
        return [Activity.model_validate(item) for item in response] 