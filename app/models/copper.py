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
    """Activity type information."""
    category: str
    id: int


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
    websites: List[HttpUrl] = Field(default_factory=list)
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
    websites: List[HttpUrl] = Field(default_factory=list)
    email_domain: Optional[str] = None
    details: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    custom_fields: List[CustomField] = Field(default_factory=list)
    industry: Optional[str] = None
    annual_revenue: Optional[float] = None
    employee_count: Optional[int] = None
    date_created: Optional[datetime] = None
    date_modified: Optional[datetime] = None
    interaction_count: Optional[int] = None


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
    """Activity entity model."""
    id: Optional[int] = None
    type: ActivityType
    details: Optional[str] = None
    activity_date: Optional[int] = None  # Unix timestamp
    parent: ParentEntity
    user_id: Optional[int] = None
    assignee_id: Optional[int] = None
    custom_fields: List[CustomField] = Field(default_factory=list)
    date_created: Optional[datetime] = None
    date_modified: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)


class ActivityCreate(Activity):
    """Model for creating new activities."""
    id: None = None
    date_created: None = None
    date_modified: None = None 