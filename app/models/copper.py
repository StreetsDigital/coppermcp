"""Copper CRM data models.

This module defines Pydantic models for Copper CRM API data structures.
These models ensure proper validation of data received from and sent to the API.
"""
from typing import List, Optional, Any, Dict, Union
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class CustomField(BaseModel):
    """Custom field data."""
    custom_field_definition_id: int = Field(gt=0)
    value: Any


class Address(BaseModel):
    """Physical address information."""
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None


class EmailPhone(BaseModel):
    """Email or phone contact information."""
    category: str  # work, home, other
    email: Optional[str] = None
    phone: Optional[str] = None


class Social(BaseModel):
    """Social media profile information."""
    category: str  # linkedin, twitter, facebook, etc.
    url: HttpUrl


class ParentEntity(BaseModel):
    """Parent entity reference."""
    type: str  # person, company, opportunity
    id: int


class ActivityType(BaseModel):
    """Activity type configuration in Copper CRM."""
    id: str
    category: str
    name: str


class Person(BaseModel):
    """Person entity model."""
    id: Optional[int] = None
    name: str
    prefix: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    suffix: Optional[str] = None
    title: Optional[str] = None
    company_name: Optional[str] = None
    company_id: Optional[int] = None
    emails: List[EmailPhone] = Field(default_factory=list)
    phone_numbers: List[EmailPhone] = Field(default_factory=list)
    socials: List[Social] = Field(default_factory=list)
    websites: List[str] = Field(default_factory=list)
    address: Optional[Address] = None
    assignee_id: Optional[int] = None
    contact_type_id: Optional[int] = None
    details: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    custom_fields: List[CustomField] = Field(default_factory=list)
    date_created: Optional[datetime] = None
    date_modified: Optional[datetime] = None
    interaction_count: Optional[int] = None


class Company(BaseModel):
    """Company entity model."""
    id: Optional[int] = None
    name: str
    assignee_id: Optional[int] = None
    address: Optional[Address] = None
    phone_numbers: List[EmailPhone] = Field(default_factory=list)
    socials: List[Social] = Field(default_factory=list)
    websites: List[HttpUrl] = Field(default_factory=list)
    email_domain: Optional[str] = None
    details: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    custom_fields: List[CustomField] = Field(default_factory=list)
    industry: Optional[str] = Field(None, pattern="^[A-Za-z0-9 &-]+$")
    annual_revenue: Optional[float] = Field(None, ge=0)
    employee_count: Optional[int] = Field(None, ge=0)
    date_created: Optional[datetime] = None
    date_modified: Optional[datetime] = None
    interaction_count: Optional[int] = Field(None, ge=0)
    primary_contact_id: Optional[int] = None
    status: Optional[str] = Field(None, pattern="^(active|inactive|prospect)$")


class Opportunity(BaseModel):
    """Opportunity entity model."""
    id: Optional[int] = None
    name: str
    assignee_id: Optional[int] = None
    company_id: Optional[int] = None
    company_name: Optional[str] = None
    primary_contact_id: Optional[int] = None
    status: str  # Open, Won, Lost, etc.
    priority: Optional[str] = None  # High, Medium, Low
    pipeline_id: Optional[int] = None
    pipeline_stage_id: Optional[int] = None
    monetary_value: Optional[float] = None
    win_probability: Optional[float] = Field(None, ge=0, le=100)
    close_date: Optional[datetime] = None
    details: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    custom_fields: List[CustomField] = Field(default_factory=list)
    date_created: Optional[datetime] = None
    date_modified: Optional[datetime] = None
    interaction_count: Optional[int] = None


class Activity(BaseModel):
    """Activity model for Copper CRM."""
    id: Optional[str] = None
    type: ActivityType
    details: Optional[str] = None
    activity_date: int = Field(description="Unix timestamp of when the activity occurred")
    user_id: str
    parent: Dict[str, str] = Field(description="Parent entity details with type and id")
    assignee_id: Optional[str] = None
    custom_fields: List[CustomField] = []
    created_at: Optional[int] = None
    updated_at: Optional[int] = None


class ActivityCreate(BaseModel):
    """Model for creating a new activity in Copper CRM."""
    type: ActivityType
    details: Optional[str] = None
    activity_date: int = Field(description="Unix timestamp of when the activity occurred")
    user_id: str
    parent: Dict[str, str] = Field(description="Parent entity details with type and id")
    assignee_id: Optional[str] = None
    custom_fields: List[CustomField] = []


class ActivityUpdate(BaseModel):
    """Model for updating an existing activity in Copper CRM."""
    type: Optional[ActivityType] = None
    details: Optional[str] = None
    activity_date: Optional[int] = None
    user_id: Optional[str] = None
    parent: Optional[Dict[str, str]] = None
    assignee_id: Optional[str] = None
    custom_fields: Optional[List[CustomField]] = None


class Task(BaseModel):
    """Copper Task model."""
    
    id: Optional[int] = None
    name: str
    related_resource: Optional[Dict[str, Any]] = None
    assignee_id: Optional[int] = None
    due_date: Optional[int] = None  # Unix timestamp
    reminder_date: Optional[int] = None  # Unix timestamp
    completed_date: Optional[int] = None  # Unix timestamp
    priority: Optional[str] = Field(None, pattern="^(none|low|medium|high)$")
    status: Optional[str] = Field(None, pattern="^(open|completed)$")
    details: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[List[Dict[str, Any]]] = None
    date_created: Optional[int] = None  # Unix timestamp
    date_modified: Optional[int] = None  # Unix timestamp


class TaskCreate(BaseModel):
    """Model for creating a new task."""
    
    name: str
    related_resource: Optional[Dict[str, Any]] = None
    assignee_id: Optional[int] = None
    due_date: Optional[int] = None
    reminder_date: Optional[int] = None
    priority: Optional[str] = Field(None, pattern="^(none|low|medium|high)$")
    details: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[List[Dict[str, Any]]] = None


class TaskUpdate(BaseModel):
    """Model for updating an existing task."""
    
    name: Optional[str] = None
    related_resource: Optional[Dict[str, Any]] = None
    assignee_id: Optional[int] = None
    due_date: Optional[int] = None
    reminder_date: Optional[int] = None
    priority: Optional[str] = Field(None, pattern="^(none|low|medium|high)$")
    status: Optional[str] = Field(None, pattern="^(open|completed)$")
    details: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[List[Dict[str, Any]]] = None


class PersonCreate(BaseModel):
    """Model for creating a new person."""
    name: str
    prefix: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    suffix: Optional[str] = None
    title: Optional[str] = None
    company_name: Optional[str] = None
    company_id: Optional[int] = None
    emails: List[EmailPhone] = Field(default_factory=list)
    phone_numbers: List[EmailPhone] = Field(default_factory=list)
    socials: List[Social] = Field(default_factory=list)
    websites: List[Social] = Field(default_factory=list)
    address: Optional[Address] = None
    assignee_id: Optional[int] = None
    contact_type_id: Optional[int] = None
    details: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    custom_fields: List[CustomField] = Field(default_factory=list)


class PersonUpdate(BaseModel):
    """Model for updating an existing person."""
    name: Optional[str] = None
    prefix: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    suffix: Optional[str] = None
    title: Optional[str] = None
    company_name: Optional[str] = None
    company_id: Optional[int] = None
    emails: Optional[List[EmailPhone]] = None
    phone_numbers: Optional[List[EmailPhone]] = None
    socials: Optional[List[Social]] = None
    websites: Optional[List[Social]] = None
    address: Optional[Address] = None
    assignee_id: Optional[int] = None
    contact_type_id: Optional[int] = None
    details: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[List[CustomField]] = None


class CompanyCreate(BaseModel):
    """Model for creating a new company."""
    name: str
    assignee_id: Optional[int] = None
    address: Optional[Address] = None
    phone_numbers: List[EmailPhone] = Field(default_factory=list)
    socials: List[Social] = Field(default_factory=list)
    websites: List[HttpUrl] = Field(default_factory=list)
    email_domain: Optional[str] = None
    details: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    custom_fields: List[CustomField] = Field(default_factory=list)
    industry: Optional[str] = Field(None, pattern="^[A-Za-z0-9 &-]+$")
    annual_revenue: Optional[float] = Field(None, ge=0)
    employee_count: Optional[int] = Field(None, ge=0)
    primary_contact_id: Optional[int] = None
    status: Optional[str] = Field(None, pattern="^(active|inactive|prospect)$")


class CompanyUpdate(BaseModel):
    """Model for updating an existing company."""
    name: Optional[str] = None
    assignee_id: Optional[int] = None
    address: Optional[Address] = None
    phone_numbers: Optional[List[EmailPhone]] = None
    socials: Optional[List[Social]] = None
    websites: Optional[List[HttpUrl]] = None
    email_domain: Optional[str] = None
    details: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[List[CustomField]] = None
    industry: Optional[str] = Field(None, pattern="^[A-Za-z0-9 &-]+$")
    annual_revenue: Optional[float] = Field(None, ge=0)
    employee_count: Optional[int] = Field(None, ge=0)
    primary_contact_id: Optional[int] = None
    status: Optional[str] = Field(None, pattern="^(active|inactive|prospect)$") 