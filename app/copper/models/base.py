"""Base models for Copper API entities.

This module provides common base models and shared components used across different
entity types in the Copper CRM API. These models define standard fields and structures
that are reused throughout the application.

Usage Examples:
    ```python
    # Create an email address
    email = Email(
        email="contact@example.com",
        category="work"
    )
    
    # Create a phone number
    phone = Phone(
        number="+1-555-123-4567",
        category="mobile"
    )
    
    # Create an address
    address = Address(
        street="123 Main St",
        city="San Francisco",
        state="CA",
        postal_code="94105",
        country="US"
    )
    
    # Create a custom field
    custom_field = CustomField(
        custom_field_definition_id=12345,
        value="High Priority"
    )
    ```

Common Field Categories:
    - Email categories: work, personal, other
    - Phone categories: work, mobile, home, other
    - Social profile types: linkedin, twitter, facebook, other
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CustomField(BaseModel):
    """Model for custom fields.
    
    This model represents a custom field value in Copper CRM. Custom fields allow
    you to store additional data specific to your organization's needs.
    
    Required Fields:
        custom_field_definition_id (int): ID of the custom field definition
        value (Any): Value of the custom field (can be string, number, boolean, etc.)
    
    Example:
        ```python
        field = CustomField(
            custom_field_definition_id=12345,
            value="Enterprise"  # Value type depends on field definition
        )
        ```
    """
    custom_field_definition_id: int
    value: Any


class Address(BaseModel):
    """Model for physical addresses.
    
    This model represents a physical address in Copper CRM.
    
    Optional Fields:
        street (str): Street address
        city (str): City name
        state (str): State/province
        postal_code (str): ZIP/postal code
        country (str): Country name
    
    Example:
        ```python
        address = Address(
            street="456 Market St",
            city="San Francisco",
            state="CA",
            postal_code="94105",
            country="US"
        )
        ```
    """
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None


class Email(BaseModel):
    """Model for email addresses.
    
    This model represents an email address with its category in Copper CRM.
    
    Required Fields:
        email (str): The email address
        category (str): Category of the email (work, personal, other)
    
    Example:
        ```python
        email = Email(
            email="sales@company.com",
            category="work"
        )
        ```
    """
    email: str
    category: str


class Phone(BaseModel):
    """Model for phone numbers.
    
    This model represents a phone number with its category in Copper CRM.
    
    Required Fields:
        number (str): The phone number
        category (str): Category of the number (work, mobile, home, other)
    
    Example:
        ```python
        phone = Phone(
            number="+1-555-987-6543",
            category="mobile"
        )
        ```
    """
    number: str
    category: str


class SocialProfile(BaseModel):
    """Model for social media profiles.
    
    This model represents a social media profile in Copper CRM.
    
    Required Fields:
        url (str): URL of the social profile
        category (str): Type of social profile (linkedin, twitter, facebook, other)
    
    Example:
        ```python
        profile = SocialProfile(
            url="https://linkedin.com/in/username",
            category="linkedin"
        )
        ```
    """
    url: str
    category: str


class BaseEntity(BaseModel):
    """Base model for Copper entities.
    
    This model provides common fields that are present in most Copper CRM entities
    like people, companies, opportunities, etc.
    
    Fields:
        id (int): Unique identifier
        name (str): Name of the entity
        date_created (int): Creation timestamp (Unix)
        date_modified (int): Last modification timestamp (Unix)
        tags (List[str]): List of tags
        custom_fields (List[CustomField]): Custom field values
    
    Example:
        ```python
        # This is typically inherited by other models, not used directly
        class Company(BaseEntity):
            # Additional company-specific fields
            pass
        ```
    """
    id: int
    name: Optional[str] = None
    date_created: Optional[int] = None
    date_modified: Optional[int] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[List[CustomField]] = None


class ActivityType(BaseModel):
    """Model for activity type."""
    category: str
    id: int = Field(default=0)  # Default to 0 for "note" type


class Parent(BaseModel):
    """Model for activity parent reference."""
    id: int
    type: str = "person"  # Default to person type 