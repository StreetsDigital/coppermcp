"""Tests for the Person transformer."""
import pytest
from datetime import datetime
from pydantic import HttpUrl

from app.mapping.person import PersonTransformer
from app.models.copper import Person, Address, EmailPhone, SocialProfile, CustomField

def test_transform_minimal_person():
    """Test transformation of person with minimal data."""
    transformer = PersonTransformer(Person)
    input_data = {
        "name": "John Doe"
    }
    
    result = transformer.transform_to_mcp(input_data)
    
    assert result["type"] == "person"
    assert result["id"] is None
    assert result["attributes"]["name"] == "John Doe"
    assert result["attributes"]["email"] is None
    assert result["attributes"]["phone"] is None
    assert result["relationships"]["company"]["data"] is None
    assert result["meta"]["interaction_count"] == 0

def test_transform_full_person():
    """Test transformation of person with all fields populated."""
    transformer = PersonTransformer(Person)
    input_data = {
        "id": 123,
        "name": "Dr. John Smith Jr.",
        "prefix": "Dr.",
        "first_name": "John",
        "last_name": "Smith",
        "suffix": "Jr.",
        "title": "CEO",
        "company_name": "ACME Corp",
        "company_id": 456,
        "assignee_id": 789,
        "details": "Important contact",
        "contact_type_id": 1,
        "emails": [
            {"email": "john@work.com", "category": "work"},
            {"email": "john@home.com", "category": "home"}
        ],
        "phone_numbers": [
            {"phone": "555-0123", "category": "work"},
            {"phone": "555-4567", "category": "mobile"}
        ],
        "socials": [
            {"url": "https://linkedin.com/in/john", "category": "linkedin"}
        ],
        "websites": ["https://johnsmith.com"],
        "tags": ["VIP", "Client"],
        "custom_fields": [
            {"custom_field_definition_id": 1, "value": "Custom Value"}
        ],
        "date_created": "2024-01-01T00:00:00Z",
        "date_modified": "2024-01-02T00:00:00Z",
        "interaction_count": 5,
        "address": {
            "street": "123 Main St",
            "city": "Springfield",
            "state": "IL",
            "postal_code": "62701",
            "country": "USA"
        }
    }
    
    result = transformer.transform_to_mcp(input_data)
    
    # Check basic attributes
    assert result["type"] == "person"
    assert result["id"] == "123"
    assert result["attributes"]["name"] == "Dr. John Smith Jr."
    assert result["attributes"]["first_name"] == "John"
    assert result["attributes"]["last_name"] == "Smith"
    assert result["attributes"]["title"] == "CEO"
    assert result["attributes"]["company"] == "ACME Corp"
    
    # Check contact info
    assert result["attributes"]["email"] == "john@work.com"
    assert result["attributes"]["phone"] == "555-0123"
    assert len(result["meta"]["additional_emails"]) == 1
    assert result["meta"]["additional_emails"][0]["email"] == "john@home.com"
    assert len(result["meta"]["additional_phones"]) == 1
    assert result["meta"]["additional_phones"][0]["phone"] == "555-4567"
    
    # Check relationships
    assert result["relationships"]["company"]["data"]["id"] == "456"
    assert result["relationships"]["assignee"]["data"]["id"] == "789"
    
    # Check address
    assert result["attributes"]["address"]["street"] == "123 Main St"
    assert result["attributes"]["address"]["city"] == "Springfield"
    assert result["attributes"]["address"]["state"] == "IL"
    
    # Check metadata
    assert result["meta"]["interaction_count"] == 5
    assert result["meta"]["contact_type_id"] == 1
    assert len(result["meta"]["social_profiles"]) == 1
    assert result["meta"]["social_profiles"][0]["category"] == "linkedin"
    assert len(result["meta"]["websites"]) == 1
    assert result["meta"]["custom_fields"]["1"] == "Custom Value"

def test_transform_work_contact_priority():
    """Test that work contact details are prioritized."""
    transformer = PersonTransformer(Person)
    input_data = {
        "name": "John Doe",
        "emails": [
            {"email": "john@personal.com", "category": "home"},
            {"email": "john@work.com", "category": "work"},
        ],
        "phone_numbers": [
            {"phone": "+1-555-1234", "category": "home"},
            {"phone": "+1-555-5678", "category": "work"},
        ]
    }
    
    result = transformer.transform_to_mcp(input_data)
    
    assert result["attributes"]["email"] == "john@work.com"
    assert result["attributes"]["phone"] == "+1-555-5678"

def test_transform_fallback_to_full_name():
    """Test fallback to full name when components not provided."""
    transformer = PersonTransformer(Person)
    input_data = {
        "name": "John Doe"  # No first_name/last_name components
    }
    
    result = transformer.transform_to_mcp(input_data)
    
    assert result["attributes"]["name"] == "John Doe"
    assert result["attributes"]["first_name"] is None
    assert result["attributes"]["last_name"] is None

def test_transform_empty_lists():
    """Test handling of empty contact lists."""
    transformer = PersonTransformer(Person)
    input_data = {
        "name": "John Doe",
        "emails": [],
        "phone_numbers": [],
        "socials": [],
        "websites": [],
        "tags": [],
        "custom_fields": []
    }
    
    result = transformer.transform_to_mcp(input_data)
    
    assert result["attributes"]["email"] is None
    assert result["attributes"]["phone"] is None
    assert result["meta"]["additional_emails"] == []
    assert result["meta"]["additional_phones"] == []
    assert result["meta"]["social_profiles"] == []
    assert result["meta"]["websites"] == []
    assert result["attributes"]["tags"] == []
    assert result["meta"]["custom_fields"] == {} 