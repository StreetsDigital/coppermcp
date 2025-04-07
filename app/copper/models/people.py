"""Models for People entities in Copper API.

This module provides models for managing people/contacts in Copper CRM. People represent
individual contacts and can be associated with companies, opportunities, and other
entities in the system.

Usage Examples:
    ```python
    # Create a new person
    person_data = PersonCreate(
        name="John Doe",
        emails=[Email(email="john@example.com", category="work")],
        title="Software Engineer",
        company_name="Tech Corp",
        phones=[Phone(number="+1-555-123-4567", category="work")],
        address=Address(
            street="123 Main St",
            city="San Francisco",
            state="CA",
            postal_code="94105"
        )
    )
    
    # Update a person
    update_data = PersonUpdate(
        title="Senior Software Engineer",
        tags=["vip", "tech"]
    )
    ```

Field Descriptions:
    - name: Full name of the person
    - emails: List of email addresses with categories
    - title: Job title or position
    - company_name: Name of the company they work for
    - phones: List of phone numbers with categories
    - address: Physical address information
    - social_profiles: List of social media profiles
    - tags: List of tags for categorizing
    - custom_fields: Custom field values specific to your Copper instance
"""
from typing import Optional, List
from pydantic import BaseModel, Field

from .base import (
    BaseEntity,
    Email,
    Phone,
    Address,
    SocialProfile,
    CustomField
)


class PersonCreate(BaseModel):
    """Model for creating a new person.
    
    This model defines the fields required and optional when creating a new person
    in Copper CRM.
    
    Required Fields:
        name (str): Full name of the person
        emails (List[Email]): At least one email address is required
    
    Optional Fields:
        title (str): Job title or position
        company_name (str): Name of the company they work for
        phones (List[Phone]): List of phone numbers
        address (Address): Physical address information
        social_profiles (List[SocialProfile]): Social media profiles
        tags (List[str]): List of tags for categorizing
        custom_fields (List[CustomField]): Custom field values
    
    Example:
        ```python
        person = PersonCreate(
            name="Jane Smith",
            emails=[
                Email(email="jane@company.com", category="work"),
                Email(email="jane@personal.com", category="personal")
            ],
            title="Product Manager",
            company_name="Tech Corp",
            phones=[Phone(number="+1-555-987-6543", category="work")],
            tags=["product", "management"]
        )
        ```
    """
    name: str
    emails: List[Email]  # List of Email objects
    title: Optional[str] = None
    company_name: Optional[str] = None
    phones: Optional[List[Phone]] = None
    address: Optional[Address] = None
    social_profiles: Optional[List[SocialProfile]] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[List[CustomField]] = None


class Person(BaseEntity):
    """Model for a person in Copper.
    
    This model represents an existing person in Copper CRM. It inherits from BaseEntity
    which provides common fields like id, name, date_created, etc.
    
    Fields:
        All fields from BaseEntity, plus:
        emails (List[Email]): List of email addresses
        title (str): Job title or position
        company_name (str): Name of the company they work for
        phones (List[Phone]): List of phone numbers
        address (Address): Physical address information
        social_profiles (List[SocialProfile]): Social media profiles
        contact_type_id (int): ID of the contact type
        assignee_id (int): ID of the assigned user
        company_id (int): ID of the associated company
        details (str): Additional notes or description
        status (str): Current status
        interaction_count (int): Number of interactions
        monetary_value (float): Associated monetary value
        converted_unit (str): Unit for monetary value
        converted_value (float): Converted monetary value
        websites (List[str]): List of associated websites
    
    Example:
        ```python
        # This is typically returned by the API, not created directly
        person = Person(
            id=12345,
            name="Jane Smith",
            emails=[Email(email="jane@company.com", category="work")],
            title="Product Manager",
            company_name="Tech Corp",
            date_created=1612345678
        )
        ```
    """
    emails: List[Email]  # List of Email objects
    title: Optional[str] = None
    company_name: Optional[str] = None
    phones: Optional[List[Phone]] = None
    address: Optional[Address] = None
    social_profiles: Optional[List[SocialProfile]] = None
    contact_type_id: Optional[int] = None
    assignee_id: Optional[int] = None
    company_id: Optional[int] = None
    details: Optional[str] = None
    status: Optional[str] = None
    interaction_count: Optional[int] = None
    monetary_value: Optional[float] = None
    converted_unit: Optional[str] = None
    converted_value: Optional[float] = None
    websites: Optional[List[str]] = None


class PersonUpdate(BaseModel):
    """Model for updating a person.
    
    This model defines what fields can be updated on an existing person. All fields
    are optional since you can update just the fields you want to change.
    
    Fields:
        name (str): Full name of the person
        emails (List[Email]): List of email addresses
        title (str): Job title or position
        company_name (str): Name of the company they work for
        phones (List[Phone]): List of phone numbers
        address (Address): Physical address information
        social_profiles (List[SocialProfile]): Social media profiles
        tags (List[str]): List of tags for categorizing
        custom_fields (List[CustomField]): Custom field values
        contact_type_id (int): ID of the contact type
        assignee_id (int): ID of the assigned user
        company_id (int): ID of the associated company
        details (str): Additional notes or description
        status (str): Current status
    
    Example:
        ```python
        update = PersonUpdate(
            title="Senior Product Manager",
            status="Active",
            tags=["product", "management", "senior"],
            details="Recently promoted to senior position"
        )
        ```
    """
    name: Optional[str] = None
    emails: Optional[List[Email]] = None  # List of Email objects
    title: Optional[str] = None
    company_name: Optional[str] = None
    phones: Optional[List[Phone]] = None
    address: Optional[Address] = None
    social_profiles: Optional[List[SocialProfile]] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[List[CustomField]] = None
    contact_type_id: Optional[int] = None
    assignee_id: Optional[int] = None
    company_id: Optional[int] = None
    details: Optional[str] = None
    status: Optional[str] = None