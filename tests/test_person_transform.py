"""Tests for the Person transformer."""
import pytest
from datetime import datetime, timezone
from typing import Dict, Any
from pydantic import HttpUrl

from app.mapping.person import PersonTransformer
from app.models.copper import Person, Address, EmailPhone, Social, CustomField
from app.models.mcp import MCPPerson

@pytest.fixture
def transformer():
    """Create a person transformer for testing."""
    return PersonTransformer(copper_model=Person, mcp_model=MCPPerson)

def test_transform_minimal_person(transformer):
    """Test transforming a person with minimal data."""
    data = {
        "id": 123,
        "name": "John Doe",
        "email": "john@example.com",
        "details": None,
        "phone_numbers": [],
        "socials": [],
        "websites": []
    }
    
    result = transformer.to_mcp(data)
    assert result["type"] == "person"
    assert result["source"] == "copper"
    assert result["source_id"] == "123"
    assert result["attributes"]["name"] == "John Doe"
    assert result["attributes"]["email"] == "john@example.com"

def test_transform_full_person(transformer):
    """Test transforming a person with all fields populated."""
    now = int(datetime.now(timezone.utc).timestamp())
    data = {
        "id": 789,
        "name": "Jane Smith",
        "email": "jane@example.com",
        "details": "Person details",
        "phone_numbers": [{"number": "123-456-7890"}],
        "socials": [{"url": "https://linkedin.com/in/janesmith"}],
        "websites": ["https://janesmith.com"],
        "date_created": now,
        "date_modified": now,
        "assignee_id": 101,
        "custom_fields": [
            {"custom_field_definition_id": 201, "value": "Custom value"}
        ]
    }
    
    result = transformer.to_mcp(data)
    assert result["type"] == "person"
    assert result["source"] == "copper"
    assert result["source_id"] == "789"
    assert result["attributes"]["name"] == "Jane Smith"
    assert result["attributes"]["email"] == "jane@example.com"
    assert result["attributes"]["details"] == "Person details"
    assert result["attributes"]["phone_numbers"][0]["number"] == "123-456-7890"
    assert result["attributes"]["socials"][0]["url"] == "https://linkedin.com/in/janesmith"
    assert result["attributes"]["websites"][0] == "https://janesmith.com"
    assert result["meta"]["custom_fields"][0]["value"] == "Custom value"

def test_transform_validation(transformer):
    """Test validation of person data."""
    data = {
        "id": 123,
        "name": "",  # Invalid empty name
        "email": "invalid-email",  # Invalid email
        "details": None,
        "phone_numbers": [],
        "socials": [],
        "websites": []
    }
    
    with pytest.raises(ValueError):
        transformer.to_mcp(data)

def test_transform_empty_custom_fields(transformer):
    """Test transforming a person with empty custom fields."""
    data = {
        "id": 123,
        "name": "John Doe",
        "email": "john@example.com",
        "details": None,
        "phone_numbers": [],
        "socials": [],
        "websites": [],
        "custom_fields": []
    }
    
    result = transformer.to_mcp(data)
    assert result["meta"]["custom_fields"] == []

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