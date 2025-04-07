"""Models for Opportunity entities in Copper API.

This module provides models for managing opportunities/deals in Copper CRM. Opportunities
represent potential sales or deals and can be associated with people, companies, and
other entities in the system.

Usage Examples:
    ```python
    # Create a new opportunity
    opportunity_data = OpportunityCreate(
        name="Enterprise Software License",
        pipeline_id=12345,
        pipeline_stage_id=67890,
        monetary_value=50000,
        close_date=int(time.time()) + 30 * 24 * 3600,  # 30 days from now
        customer_source_id=45678,
        primary_contact_id=98765
    )
    
    # Update an opportunity
    update_data = OpportunityUpdate(
        monetary_value=75000,
        win_probability=80,
        tags=["enterprise", "software"]
    )
    ```

Field Descriptions:
    - name: Name/title of the opportunity
    - pipeline_id: ID of the pipeline this opportunity belongs to
    - pipeline_stage_id: ID of the current stage in the pipeline
    - monetary_value: Value of the opportunity in default currency
    - close_date: Expected close date (Unix timestamp)
    - customer_source_id: ID of the lead source
    - primary_contact_id: ID of the primary contact person
    - company_id: ID of the associated company
    - loss_reason_id: ID of the reason if opportunity is lost
    - win_probability: Percentage probability of winning (0-100)
    - priority: Priority level of the opportunity
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_serializer

from .base import BaseEntity, CustomField


class Pipeline(BaseModel):
    """Model for pipeline data."""
    id: int
    name: Optional[str] = None
    stages: Optional[List[dict]] = None
    is_revenue: Optional[bool] = None
    type: Optional[str] = Field(None, pattern="^(opportunity|project|item)$")


class OpportunityCreate(BaseModel):
    """Model for creating a new opportunity.
    
    This model defines the fields required and optional when creating a new opportunity
    in Copper CRM.
    
    Required Fields:
        name (str): Name/title of the opportunity
        pipeline_id (int): ID of the pipeline this opportunity belongs to
        pipeline_stage_id (int): ID of the current stage in the pipeline
    
    Optional Fields:
        monetary_value (float): Value of the opportunity
        close_date (int): Expected close date as Unix timestamp
        customer_source_id (int): ID of the lead source
        primary_contact_id (int): ID of the primary contact person
        company_id (int): ID of the associated company
        loss_reason_id (int): ID of the reason if opportunity is lost
        win_probability (int): Percentage probability of winning (0-100)
        priority (str): Priority level
        tags (List[str]): List of tags for categorizing
        custom_fields (List[CustomField]): Custom field values
        details (str): Additional notes or description
    
    Example:
        ```python
        opportunity = OpportunityCreate(
            name="Software License Deal",
            pipeline_id=12345,
            pipeline_stage_id=67890,
            monetary_value=100000.00,
            close_date=1640995200,  # Dec 31, 2021
            win_probability=75,
            tags=["software", "enterprise"]
        )
        ```
    """
    name: str
    primary_contact_id: int  # Required field
    pipeline_id: int
    pipeline_stage_id: int
    monetary_value: Optional[float] = None
    close_date: Optional[datetime] = None
    customer_source_id: Optional[int] = None
    loss_reason_id: Optional[int] = None
    company_id: Optional[int] = None
    assignee_id: Optional[int] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[List[CustomField]] = None
    details: Optional[str] = None
    priority: Optional[str] = Field(None, pattern="^(None|Low|Medium|High)$")
    status: Optional[str] = Field(None, pattern="^(Open|Won|Lost|Abandoned)$")
    win_probability: Optional[int] = Field(None, ge=0, le=100)

    @field_serializer('close_date')
    def serialize_close_date(self, close_date: Optional[datetime]) -> Optional[int]:
        """Serialize close_date to Unix timestamp."""
        if close_date is None:
            return None
        return int(close_date.timestamp())


class Opportunity(BaseEntity):
    """Model for an opportunity in Copper.
    
    This model represents an existing opportunity in Copper CRM. It inherits from BaseEntity
    which provides common fields like id, name, date_created, etc.
    
    Fields:
        All fields from BaseEntity, plus:
        pipeline_id (int): ID of the pipeline
        pipeline_stage_id (int): ID of the current stage
        monetary_value (float): Value of the opportunity
        close_date (int): Expected close date
        customer_source_id (int): ID of the lead source
        primary_contact_id (int): ID of the primary contact
        company_id (int): ID of the associated company
        loss_reason_id (int): ID of the reason if lost
        win_probability (int): Probability of winning (0-100)
        priority (str): Priority level
        interaction_count (int): Number of interactions
        status (str): Current status
    
    Example:
        ```python
        # This is typically returned by the API, not created directly
        opportunity = Opportunity(
            id=12345,
            name="Enterprise Deal",
            pipeline_id=67890,
            pipeline_stage_id=45678,
            monetary_value=250000.00,
            win_probability=80,
            status="Open",
            date_created=1612345678
        )
        ```
    """
    pipeline_id: int
    pipeline_stage_id: int
    primary_contact_id: int
    monetary_value: Optional[float] = None
    close_date: Optional[datetime] = None
    customer_source_id: Optional[int] = None
    loss_reason_id: Optional[int] = None
    company_id: Optional[int] = None
    company_name: Optional[str] = None
    assignee_id: Optional[int] = None
    details: Optional[str] = None
    priority: Optional[str] = Field(None, pattern="^(None|Low|Medium|High)$")
    status: Optional[str] = Field(None, pattern="^(Open|Won|Lost|Abandoned)$")
    win_probability: Optional[int] = Field(None, ge=0, le=100)
    interaction_count: Optional[int] = None
    pipeline: Optional[Pipeline] = None
    pipeline_stage: Optional[dict] = None
    customer_source: Optional[dict] = None
    loss_reason: Optional[dict] = None
    pipeline_is_revenue: Optional[bool] = None
    pipeline_type: Optional[str] = Field(None, pattern="^(opportunity|project|item)$")

    @field_serializer('close_date')
    def serialize_close_date(self, close_date: Optional[datetime]) -> Optional[int]:
        """Serialize close_date to Unix timestamp."""
        if close_date is None:
            return None
        return int(close_date.timestamp())


class OpportunityUpdate(BaseModel):
    """Model for updating an opportunity.
    
    This model defines what fields can be updated on an existing opportunity. All fields
    are optional since you can update just the fields you want to change.
    
    Fields:
        name (str): Name/title of the opportunity
        pipeline_id (int): ID of the pipeline
        pipeline_stage_id (int): ID of the current stage
        monetary_value (float): Value of the opportunity
        close_date (int): Expected close date
        customer_source_id (int): ID of the lead source
        primary_contact_id (int): ID of the primary contact
        company_id (int): ID of the associated company
        loss_reason_id (int): ID of the reason if lost
        win_probability (int): Probability of winning (0-100)
        priority (str): Priority level
        tags (List[str]): List of tags
        custom_fields (List[CustomField]): Custom field values
        details (str): Additional notes
    
    Example:
        ```python
        update = OpportunityUpdate(
            monetary_value=300000.00,
            win_probability=90,
            pipeline_stage_id=98765,
            tags=["enterprise", "q4-2023"],
            details="Final negotiation phase"
        )
        ```
    """
    name: Optional[str] = None
    primary_contact_id: Optional[int] = None
    pipeline_id: Optional[int] = None
    pipeline_stage_id: Optional[int] = None
    monetary_value: Optional[float] = None
    close_date: Optional[datetime] = None
    customer_source_id: Optional[int] = None
    loss_reason_id: Optional[int] = None
    company_id: Optional[int] = None
    assignee_id: Optional[int] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[List[CustomField]] = None
    details: Optional[str] = None
    priority: Optional[str] = Field(None, pattern="^(None|Low|Medium|High)$")
    status: Optional[str] = Field(None, pattern="^(Open|Won|Lost|Abandoned)$")
    win_probability: Optional[int] = Field(None, ge=0, le=100)

    @field_serializer('close_date')
    def serialize_close_date(self, close_date: Optional[datetime]) -> Optional[int]:
        """Serialize close_date to Unix timestamp."""
        if close_date is None:
            return None
        return int(close_date.timestamp()) 