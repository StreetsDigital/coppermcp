"""Models for Activity entities in Copper API.

This module provides models for managing activities in Copper CRM. Activities represent
interactions with contacts, such as emails, meetings, notes, or tasks. They can be
associated with people, companies, opportunities, and other entities in the system.

Usage Examples:
    ```python
    # Create a new activity
    activity_data = ActivityCreate(
        type=ActivityType(category="user", id=12345),
        details="Met with client to discuss requirements",
        parent=RelatedResource(
            id=67890,
            type="opportunity"
        )
    )
    
    # Update an activity
    update_data = ActivityUpdate(
        details="Updated meeting notes with action items",
        activity_date=int(time.time())
    )
    ```

Field Descriptions:
    - type: Activity type information (category and ID)
    - details: Description or content of the activity
    - parent: Related entity this activity is associated with
    - activity_date: When the activity occurred (Unix timestamp)
    - user_id: ID of the user who performed the activity
    - assignee_id: ID of the user the activity is assigned to
    - custom_fields: Custom field values specific to your Copper instance
"""
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field

from .base import BaseEntity, Parent, CustomField


class ActivityType(BaseModel):
    """Model for specifying the type of an activity.
    
    This model defines the category and ID of an activity type in Copper CRM.
    Currently, only the 'user' category is supported.
    
    Required Fields:
        category (str): Category of the activity (must be 'user')
        id (int): ID of the activity type
    
    Example:
        ```python
        activity_type = ActivityType(
            category="user",
            id=12345  # ID of a specific activity type like 'meeting' or 'note'
        )
        ```
    """
    category: Literal["user"] = Field(description="Category of the activity (must be 'user')")
    id: int = Field(description="ID of the activity type")


class RelatedResource(BaseModel):
    """Model for specifying a related entity.
    
    This model defines the relationship between an activity and another entity
    in Copper CRM (like a person, company, or opportunity).
    
    Required Fields:
        id (int): ID of the related entity
        type (str): Type of the related entity ('person', 'company', 'opportunity', etc.)
    
    Example:
        ```python
        related = RelatedResource(
            id=12345,
            type="opportunity"  # Can be 'person', 'company', 'opportunity', etc.
        )
        ```
    """
    id: int
    type: str


class ActivityCreate(BaseModel):
    """Model for creating a new activity.
    
    This model defines the fields required and optional when creating a new activity
    in Copper CRM.
    
    Required Fields:
        type (ActivityType): Type information for the activity
        details (str): Description or content of the activity
        parent (RelatedResource): Entity this activity is related to
    
    Optional Fields:
        activity_date (int): When the activity occurred (Unix timestamp)
        user_id (int): ID of the user who performed the activity
        assignee_id (int): ID of the user the activity is assigned to
        custom_fields (List[CustomField]): Custom field values
    
    Example:
        ```python
        activity = ActivityCreate(
            type=ActivityType(category="user", id=12345),
            details="Phone call with client about new features",
            parent=RelatedResource(id=67890, type="person"),
            activity_date=int(time.time()),
            assignee_id=45678
        )
        ```
    """
    type: ActivityType
    details: str
    parent: RelatedResource
    activity_date: Optional[int] = None
    user_id: Optional[int] = None
    assignee_id: Optional[int] = None
    custom_fields: Optional[List[CustomField]] = None


class Activity(BaseEntity):
    """Model for an activity in Copper.
    
    This model represents an existing activity in Copper CRM. It inherits from BaseEntity
    which provides common fields like id, date_created, etc.
    
    Fields:
        All fields from BaseEntity, plus:
        type (ActivityType): Type information
        details (str): Description or content
        parent (RelatedResource): Related entity
        activity_date (int): When it occurred
        user_id (int): User who performed it
        assignee_id (int): User it's assigned to
        custom_fields (List[CustomField]): Custom field values
    
    Example:
        ```python
        # This is typically returned by the API, not created directly
        activity = Activity(
            id=12345,
            type=ActivityType(category="user", id=67890),
            details="Client meeting notes",
            parent=RelatedResource(id=45678, type="opportunity"),
            activity_date=1612345678,
            date_created=1612345678
        )
        ```
    """
    type: ActivityType
    details: str
    parent: RelatedResource
    activity_date: Optional[int] = None
    user_id: Optional[int] = None
    assignee_id: Optional[int] = None
    custom_fields: Optional[List[CustomField]] = None


class ActivityUpdate(BaseModel):
    """Model for updating an activity.
    
    This model defines what fields can be updated on an existing activity. All fields
    are optional since you can update just the fields you want to change.
    
    Fields:
        type (ActivityType): Type information
        details (str): Description or content
        parent (RelatedResource): Related entity
        activity_date (int): When it occurred
        user_id (int): User who performed it
        assignee_id (int): User it's assigned to
        custom_fields (List[CustomField]): Custom field values
    
    Example:
        ```python
        update = ActivityUpdate(
            details="Updated meeting notes with follow-up items",
            activity_date=int(time.time()),
            custom_fields=[
                CustomField(
                    custom_field_definition_id=12345,
                    value="High priority"
                )
            ]
        )
        ```
    """
    type: Optional[ActivityType] = None
    details: Optional[str] = None
    parent: Optional[RelatedResource] = None
    activity_date: Optional[int] = None
    user_id: Optional[int] = None
    assignee_id: Optional[int] = None
    custom_fields: Optional[List[CustomField]] = None 