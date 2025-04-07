"""Client for managing Tasks in Copper API."""
from typing import Optional, List, Dict, Any, Union

from ..base import CopperBaseClient
from ..models import Task, TaskCreate, TaskUpdate


class TasksClient:
    """Client for managing Tasks in Copper API."""

    ENDPOINT = "tasks"

    def __init__(self, base_client: CopperBaseClient):
        """Initialize the Tasks client.
        
        Args:
            base_client: The base Copper client for making HTTP requests
        """
        self.base_client = base_client

    def get(self, task_id: int) -> Task:
        """Fetch a task by ID.
        
        Args:
            task_id: The ID of the task to fetch
            
        Returns:
            Task: The requested task
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self.base_client._get(f"{self.ENDPOINT}/{task_id}")
        return Task.model_validate(response)

    def create(self, data: TaskCreate) -> Task:
        """Create a new task.
        
        Args:
            data: The task data
            
        Returns:
            Task: The created task
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self.base_client._post(self.ENDPOINT, json=data.model_dump(exclude_none=True))
        return Task.model_validate(response)

    def update(self, task_id: int, data: TaskUpdate) -> Task:
        """Update an existing task.
        
        Args:
            task_id: The ID of the task to update
            data: The task data to update
            
        Returns:
            Task: The updated task
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        response = self.base_client._put(
            f"{self.ENDPOINT}/{task_id}",
            json=data.model_dump(exclude_none=True)
        )
        return Task.model_validate(response)

    def delete(self, task_id: int) -> None:
        """Delete a task.
        
        Args:
            task_id: The ID of the task to delete
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        self.base_client._delete(f"{self.ENDPOINT}/{task_id}")

    def list(
        self,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_direction: Optional[str] = None,
        filter_by: Optional[Dict[str, Any]] = None
    ) -> List[Task]:
        """List tasks with optional filtering and pagination.
        
        Args:
            page_size: Number of records to return per page
            page_number: Page number to return
            sort_by: Field to sort by
            sort_direction: Sort direction ('asc' or 'desc')
            filter_by: Dictionary of fields to filter by
            
        Returns:
            List[Task]: List of tasks matching the criteria
            
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
        return [Task.model_validate(item) for item in response] 