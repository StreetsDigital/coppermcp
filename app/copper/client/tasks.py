"""Tasks client for the Copper API.

AI Usage Guide:
--------------
Common task-related requests and how to handle them:

1. List/Search Tasks:
   "Show me my outstanding tasks"
   ```python
   tasks = await client.tasks.search({
       "is_complete": False,
       "assignee_id": current_user_id
   })
   ```

   "Find tasks due this week"
   ```python
   week_start = datetime.now().replace(hour=0, minute=0)
   week_end = week_start + timedelta(days=7)
   tasks = await client.tasks.search({
       "due_date_start": int(week_start.timestamp()),
       "due_date_end": int(week_end.timestamp())
   })
   ```

2. Create Tasks:
   "Create a task to follow up with John Smith next Tuesday"
   ```python
   # First find the person
   people = await client.people.search({"name": "John Smith"})
   person_id = people[0].id if people else None

   # Calculate next Tuesday
   today = datetime.now()
   days_ahead = 1 - today.weekday() + 1  # 1 = Tuesday
   if days_ahead <= 0:
       days_ahead += 7
   next_tuesday = today + timedelta(days=days_ahead)

   task = await client.tasks.create(TaskCreate(
       name="Follow up with John Smith",
       due_date=int(next_tuesday.timestamp()),
       related_resource={"id": person_id, "type": "person"} if person_id else None
   ))
   ```

3. Update Tasks:
   "Mark task as complete"
   ```python
   task = await client.tasks.update(task_id, {"is_complete": True})
   ```

   "Change task priority to high"
   ```python
   task = await client.tasks.update(task_id, {"priority": "high"})
   ```

4. Delete Tasks:
   "Delete the follow-up task"
   ```python
   await client.tasks.delete(task_id)
   ```

Common Patterns:
- Always validate task_id exists before update/delete
- Check for existing similar tasks before creating
- Consider timezone when working with dates
- Link tasks to relevant people/companies/opportunities
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from .base import CopperClient

from ..models.tasks import Task, TaskCreate, TaskUpdate


class TasksClient:
    """Client for managing tasks in Copper CRM."""
    
    def __init__(self, client: CopperClient):
        """Initialize the tasks client.
        
        Args:
            client: The base Copper client
        """
        self.client = client
    
    async def list(
        self,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """List tasks.
        
        Args:
            page_size: Number of records to return per page
            page_number: Page number to return
            
        Returns:
            List[Dict[str, Any]]: List of tasks
        """
        params = {}
        if page_size is not None:
            params["page_size"] = page_size
        if page_number is not None:
            params["page_number"] = page_number
            
        return await self.client.get("/tasks", params=params)
    
    async def get(self, task_id: int) -> Dict[str, Any]:
        """Get a task by ID.
        
        Args:
            task_id: ID of the task
            
        Returns:
            Dict[str, Any]: Task details
        """
        return await self.client.get(f"/tasks/{task_id}")
    
    async def create(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task.
        
        Args:
            task: Task data
            
        Returns:
            Dict[str, Any]: Created task
        """
        return await self.client.post("/tasks", json=task)
    
    async def update(self, task_id: int, task: Dict[str, Any]) -> Dict[str, Any]:
        """Update a task.
        
        Args:
            task_id: ID of the task to update
            task: Updated task data
            
        Returns:
            Dict[str, Any]: Updated task
        """
        return await self.client.put(f"/tasks/{task_id}", json=task)
    
    async def delete(self, task_id: int) -> None:
        """Delete a task.
        
        Args:
            task_id: ID of the task to delete
        """
        await self.client.delete(f"/tasks/{task_id}")
    
    async def search(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for tasks.
        
        Args:
            query: Search criteria
            
        Returns:
            List[Dict[str, Any]]: Matching tasks
        """
        return await self.client.post("/tasks/search", json=query) 