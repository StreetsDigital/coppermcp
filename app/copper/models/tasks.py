"""Models for Task entities in Copper API.

This module provides models for managing tasks in Copper CRM. Tasks are used to track
to-do items and can be associated with various entities like leads, people, companies,
opportunities, or projects.

Usage Examples:
    ```python
    # Create a new task
    task_data = TaskCreate(
        name="Follow up with client",
        related_resource=RelatedResource(
            id=opportunity_id,
            type="opportunity"
        ),
        assignee_id=user_id,
        due_date=datetime.now() + timedelta(days=7),
        priority="High",
        status="Open"
    )
    
    # Update a task
    update_data = TaskUpdate(
        name="Updated task name",
        status="Completed"
    )
    ```

Field Descriptions:
    - name: The title/name of the task
    - related_resource: The entity this task is associated with (lead, person, company, etc.)
    - assignee_id: The ID of the user assigned to this task
    - due_date: When the task is due
    - reminder_date: When to send a reminder about the task
    - priority: Task priority (None, Low, Medium, High)
    - status: Task status (Open, Completed)
    - details: Additional notes or description
    - tags: List of tags for categorizing the task
    - custom_fields: Custom field values specific to your Copper instance
"""
from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field, field_serializer

from .base import BaseEntity, CustomField, Parent


class RelatedResource(BaseModel):
    """Model for task related resource.
    
    This model defines what entity (lead, person, company, etc.) a task is related to.
    
    Fields:
        id (int): The ID of the related entity
        type (str): The type of entity. Must be one of:
            - "lead": A potential customer
            - "person": An individual contact
            - "company": A company/organization
            - "opportunity": A sales opportunity
            - "project": A project
            - "task": Another task
    
    Example:
        ```python
        related = RelatedResource(
            id=12345,
            type="opportunity"
        )
        ```
    """
    id: int
    type: str = Field(..., pattern="^(lead|person|company|opportunity|project|task)$")


class TaskCreate(BaseModel):
    """Model for creating a new task.
    
    This model defines the fields required and optional when creating a new task
    in Copper CRM.
    
    Required Fields:
        name (str): The title/name of the task
    
    Optional Fields:
        related_resource (RelatedResource): The entity this task is associated with
        assignee_id (int): The ID of the user assigned to this task
        due_date (datetime): When the task is due
        reminder_date (datetime): When to send a reminder
        priority (str): Task priority (None, Low, Medium, High)
        status (str): Task status (Open, Completed)
        details (str): Additional notes or description
        tags (List[str]): List of tags for categorizing
        custom_fields (List[CustomField]): Custom field values
    
    Example:
        ```python
        task = TaskCreate(
            name="Follow up with client",
            related_resource=RelatedResource(id=12345, type="opportunity"),
            assignee_id=67890,
            due_date=datetime.now() + timedelta(days=7),
            priority="High",
            status="Open"
        )
        ```
    """
    name: str
    related_resource: Optional[RelatedResource] = None
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None
    reminder_date: Optional[datetime] = None
    priority: Optional[str] = Field(None, pattern="^(None|Low|Medium|High)$")
    status: Optional[str] = Field(None, pattern="^(Open|Completed)$")
    details: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[List[CustomField]] = None

    @field_serializer('due_date', 'reminder_date')
    def serialize_dates(self, value: Optional[datetime], _info) -> Optional[int]:
        """Serialize dates to Unix timestamp."""
        if value is None:
            return None
        return int(value.timestamp())


class Task(BaseEntity):
    """Model for a task in Copper.
    
    This model represents an existing task in Copper CRM. It inherits from BaseEntity
    which provides common fields like id, name, date_created, etc.
    
    Fields:
        All fields from BaseEntity, plus:
        related_resource (RelatedResource): The entity this task is associated with
        assignee_id (int): The ID of the user assigned to this task
        due_date (datetime): When the task is due
        reminder_date (datetime): When to send a reminder
        completed_date (datetime): When the task was completed
        priority (str): Task priority (None, Low, Medium, High)
        status (str): Task status (Open, Completed)
        details (str): Additional notes or description
    
    Example:
        ```python
        # This is typically returned by the API, not created directly
        task = Task(
            id=12345,
            name="Follow up with client",
            related_resource=RelatedResource(id=67890, type="opportunity"),
            status="Open",
            priority="High",
            date_created=1612345678
        )
        ```
    """
    related_resource: Optional[RelatedResource] = None
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None
    reminder_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    priority: Optional[str] = Field(None, pattern="^(None|Low|Medium|High)$")
    status: Optional[str] = Field(None, pattern="^(Open|Completed)$")
    details: Optional[str] = None

    @field_serializer('due_date', 'reminder_date', 'completed_date')
    def serialize_dates(self, value: Optional[datetime], _info) -> Optional[int]:
        """Serialize dates to Unix timestamp."""
        if value is None:
            return None
        return int(value.timestamp())


class TaskUpdate(BaseModel):
    """Model for updating a task.
    
    This model defines what fields can be updated on an existing task. All fields
    are optional since you can update just the fields you want to change.
    
    Fields:
        name (str): The title/name of the task
        related_resource (RelatedResource): The entity this task is associated with
        assignee_id (int): The ID of the user assigned to this task
        due_date (datetime): When the task is due
        reminder_date (datetime): When to send a reminder
        priority (str): Task priority (None, Low, Medium, High)
        status (str): Task status (Open, Completed)
        details (str): Additional notes or description
        tags (List[str]): List of tags for categorizing
        custom_fields (List[CustomField]): Custom field values
    
    Example:
        ```python
        update = TaskUpdate(
            status="Completed",
            details="Updated with final notes"
        )
        ```
    """
    name: Optional[str] = None
    related_resource: Optional[RelatedResource] = None
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None
    reminder_date: Optional[datetime] = None
    priority: Optional[str] = Field(None, pattern="^(None|Low|Medium|High)$")
    status: Optional[str] = Field(None, pattern="^(Open|Completed)$")
    details: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[List[CustomField]] = None

    @field_serializer('due_date', 'reminder_date')
    def serialize_dates(self, value: Optional[datetime], _info) -> Optional[int]:
        """Serialize dates to Unix timestamp."""
        if value is None:
            return None
        return int(value.timestamp()) 