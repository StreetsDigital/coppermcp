"""Models for Company entities in Copper API.

This module provides models for managing companies/organizations in Copper CRM. Companies
represent organizations that you do business with and can be associated with people,
opportunities, and other entities in the system.

Usage Examples:
    ```python
    # Create a new company
    company_data = CompanyCreate(
        name="Tech Corp",
        emails=[Email(email="info@techcorp.com", category="work")],
        phones=[Phone(number="+1-555-123-4567", category="main")],
        address=Address(
            street="123 Tech Ave",
            city="San Francisco",
            state="CA",
            postal_code="94105"
        ),
        websites=["https://techcorp.com"]
    )
    
    # Update a company
    update_data = CompanyUpdate(
        details="Major enterprise client",
        tags=["enterprise", "tech"]
    )
    ```

Field Descriptions:
    - name: Name of the company
    - emails: List of email addresses with categories
    - phones: List of phone numbers with categories
    - address: Physical address information
    - social_profiles: List of social media profiles
    - websites: List of company websites
    - tags: List of tags for categorizing
    - custom_fields: Custom field values specific to your Copper instance
    - details: Additional notes or description
"""
from typing import Optional, List
from pydantic import BaseModel

from .base import (
    BaseEntity,
    Email,
    Phone,
    Address,
    SocialProfile,
    CustomField
)


class CompanyCreate(BaseModel):
    """Model for creating a new company.
    
    This model defines the fields required and optional when creating a new company
    in Copper CRM.
    
    Required Fields:
        name (str): Name of the company
    
    Optional Fields:
        emails (List[Email]): List of email addresses
        phones (List[Phone]): List of phone numbers
        address (Address): Physical address information
        social_profiles (List[SocialProfile]): Social media profiles
        websites (List[str]): List of company websites
        tags (List[str]): List of tags for categorizing
        custom_fields (List[CustomField]): Custom field values
        details (str): Additional notes or description
    
    Example:
        ```python
        company = CompanyCreate(
            name="Acme Corp",
            emails=[Email(email="info@acme.com", category="work")],
            phones=[
                Phone(number="+1-555-123-4567", category="main"),
                Phone(number="+1-555-987-6543", category="sales")
            ],
            websites=["https://acme.com"],
            tags=["manufacturing", "enterprise"]
        )
        ```
    """
    name: str
    emails: Optional[List[Email]] = None
    phones: Optional[List[Phone]] = None
    address: Optional[Address] = None
    social_profiles: Optional[List[SocialProfile]] = None
    websites: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[List[CustomField]] = None
    details: Optional[str] = None


class Company(BaseEntity):
    """Model for a company in Copper.
    
    This model represents an existing company in Copper CRM. It inherits from BaseEntity
    which provides common fields like id, name, date_created, etc.
    
    Fields:
        All fields from BaseEntity, plus:
        emails (List[Email]): List of email addresses
        phones (List[Phone]): List of phone numbers
        address (Address): Physical address information
        social_profiles (List[SocialProfile]): Social media profiles
        websites (List[str]): List of company websites
        assignee_id (int): ID of the assigned user
        contact_type_id (int): ID of the contact type
        details (str): Additional notes or description
        interaction_count (int): Number of interactions
        status (str): Current status
    
    Example:
        ```python
        # This is typically returned by the API, not created directly
        company = Company(
            id=12345,
            name="Acme Corp",
            emails=[Email(email="info@acme.com", category="work")],
            websites=["https://acme.com"],
            status="Active",
            date_created=1612345678
        )
        ```
    """
    emails: Optional[List[Email]] = None
    phones: Optional[List[Phone]] = None
    address: Optional[Address] = None
    social_profiles: Optional[List[SocialProfile]] = None
    websites: Optional[List[str]] = None
    assignee_id: Optional[int] = None
    contact_type_id: Optional[int] = None
    details: Optional[str] = None
    interaction_count: Optional[int] = None
    status: Optional[str] = None


class CompanyUpdate(BaseModel):
    """Model for updating a company.
    
    This model defines what fields can be updated on an existing company. All fields
    are optional since you can update just the fields you want to change.
    
    Fields:
        name (str): Name of the company
        emails (List[Email]): List of email addresses
        phones (List[Phone]): List of phone numbers
        address (Address): Physical address information
        social_profiles (List[SocialProfile]): Social media profiles
        websites (List[str]): List of company websites
        tags (List[str]): List of tags for categorizing
        custom_fields (List[CustomField]): Custom field values
        assignee_id (int): ID of the assigned user
        contact_type_id (int): ID of the contact type
        details (str): Additional notes or description
        status (str): Current status
    
    Example:
        ```python
        update = CompanyUpdate(
            name="Acme Corporation",
            status="Active",
            details="Global enterprise client",
            tags=["enterprise", "global"],
            assignee_id=67890
        )
        ```
    """
    name: Optional[str] = None
    emails: Optional[List[Email]] = None
    phones: Optional[List[Phone]] = None
    address: Optional[Address] = None
    social_profiles: Optional[List[SocialProfile]] = None
    websites: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[List[CustomField]] = None
    assignee_id: Optional[int] = None
    contact_type_id: Optional[int] = None
    details: Optional[str] = None
    status: Optional[str] = None 