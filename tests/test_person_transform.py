"""Tests for the Person transformer."""
import pytest
from datetime import datetime, timezone
from typing import Dict, Any
from pydantic import HttpUrl
from pydantic_core import ValidationError

from app.mapping.person import PersonTransformer
from app.models.copper import Person, Address, EmailPhone, Social, CustomField
from app.models.mcp import MCPPerson

@pytest.fixture
def transformer():
    """Create a person transformer for testing."""
    return PersonTransformer(copper_model=Person, mcp_model=MCPPerson)

@pytest.fixture
def mock_person():
    """Create a mock person with all fields."""
    return Person(
        id=12345,
        name="John Doe",
        emails=[
            EmailPhone(email="john@work.com", category="work"),
            EmailPhone(email="john@personal.com", category="personal")
        ],
        phone_numbers=[
            EmailPhone(phone="+1234567890", category="work"),
            EmailPhone(phone="+0987654321", category="mobile")
        ],
        socials=[
            Social(url="https://linkedin.com/johndoe", category="linkedin")
        ],
        websites=["https://johndoe.com"],
        address=Address(
            street="123 Main St",
            city="San Francisco",
            state="CA",
            postal_code="94105",
            country="US"
        ),
        assignee_id=67890,
        contact_type_id=1,
        details="Test person details",
        tags=["test", "person"],
        custom_fields=[
            CustomField(
                custom_field_definition_id=1,
                value="Custom value 1"
            )
        ]
    )

def test_transform_minimal_person(transformer):
    """Test transforming a person with minimal data."""
    data = {
        "id": 123,
        "name": "John Doe",
        "emails": [{"email": "john@example.com", "category": "work"}],
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
    assert result["attributes"]["first_name"] == "John"
    assert result["attributes"]["last_name"] == "Doe"
    assert result["attributes"]["email"] == "john@example.com"
    assert result["attributes"]["phone"] is None
    assert result["attributes"]["socials"] == []
    assert result["attributes"]["websites"] == []
    assert result["meta"]["custom_fields"] == {}

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
        "emails": [{"email": "invalid-email", "category": "work"}],  # Invalid email
        "details": None,
        "phone_numbers": [],
        "socials": [],
        "websites": []
    }

    with pytest.raises(ValidationError):
        transformer.to_mcp(data)

def test_transform_empty_custom_fields(transformer):
    """Test transforming a person with empty custom fields."""
    data = {
        "id": 123,
        "name": "John Doe",
        "emails": [{"email": "john@example.com", "category": "work"}],
        "details": None,
        "phone_numbers": [],
        "socials": [],
        "websites": [],
        "custom_fields": []
    }
    
    result = transformer.to_mcp(data)
    assert result["meta"]["custom_fields"] == {}

def test_transform_work_contact_priority():
    """Test that work contact details are prioritized."""
    transformer = PersonTransformer(copper_model=Person, mcp_model=MCPPerson)
    person = Person(
        id=123,
        name="John Doe",
        emails=[
            EmailPhone(email="personal@example.com", category="personal"),
            EmailPhone(email="work@example.com", category="work")
        ],
        phone_numbers=[
            EmailPhone(phone="+1234567890", category="mobile"),
            EmailPhone(phone="+0987654321", category="work")
        ]
    )
    result = transformer.to_mcp(person)
    assert result["attributes"]["email"] == "work@example.com"
    assert result["attributes"]["phone"] == "+0987654321"

def test_transform_fallback_to_full_name():
    """Test fallback to full name when components not provided."""
    transformer = PersonTransformer(copper_model=Person, mcp_model=MCPPerson)
    person = Person(
        id=123,
        name="John Smith Doe"
    )
    result = transformer.to_mcp(person)
    assert result["attributes"]["first_name"] == "John"
    assert result["attributes"]["last_name"] == "Smith Doe"

def test_transform_empty_lists(transformer):
    """Test handling of empty contact lists."""
    person = Person(
        id=123,
        name="John Doe"
    )
    result = transformer.to_mcp(person)
    assert result["attributes"]["email"] is None
    assert result["attributes"]["phone"] is None
    assert result["attributes"]["socials"] == []
    assert result["attributes"]["websites"] == []

def test_transform_from_copper(transformer):
    """Test transforming Copper data to a Person model."""
    copper_data = {
        "id": 12345,
        "name": "John Doe",
        "attributes": {
            "emails": [{"email": "john@work.com", "category": "work"}],
            "phone_numbers": [{"phone": "+1234567890", "category": "work"}],
            "socials": [{"url": "https://linkedin.com/johndoe", "category": "linkedin"}],
            "websites": ["https://johndoe.com"],
            "address": {
                "street": "123 Main St",
                "city": "San Francisco",
                "state": "CA",
                "postal_code": "94105",
                "country": "US"
            },
            "assignee_id": 67890,
            "contact_type_id": 1,
            "details": "Test person details",
            "tags": ["test", "person"]
        },
        "custom_fields": [
            {
                "custom_field_definition_id": 1,
                "value": "Custom value 1"
            }
        ]
    }

    result = transformer.from_copper(copper_data)
    assert result.id == 12345
    assert result.name == "John Doe"
    assert len(result.emails) == 1
    assert result.emails[0].email == "john@work.com"
    assert result.emails[0].category == "work"
    assert len(result.phone_numbers) == 1
    assert result.phone_numbers[0].phone == "+1234567890"
    assert result.phone_numbers[0].category == "work"
    assert len(result.socials) == 1
    assert str(result.socials[0].url) == "https://linkedin.com/johndoe"
    assert result.socials[0].category == "linkedin"
    assert len(result.websites) == 1
    assert result.websites[0] == "https://johndoe.com"
    assert result.address.street == "123 Main St"
    assert result.address.city == "San Francisco"
    assert result.address.state == "CA"
    assert result.address.postal_code == "94105"
    assert result.address.country == "US"
    assert result.assignee_id == 67890
    assert result.contact_type_id == 1
    assert result.details == "Test person details"
    assert result.tags == ["test", "person"]
    assert len(result.custom_fields) == 1
    assert result.custom_fields[0].custom_field_definition_id == 1
    assert result.custom_fields[0].value == "Custom value 1"

def test_primary_contact_extraction(transformer):
    """Test extraction of primary contact information."""
    person = Person(
        id=12345,
        name="John Doe",
        emails=[
            EmailPhone(email="primary@work.com", category="work"),
            EmailPhone(email="secondary@personal.com", category="personal")
        ],
        phone_numbers=[
            EmailPhone(phone="+1234567890", category="work"),
            EmailPhone(phone="+0987654321", category="mobile")
        ]
    )

    result = transformer.to_copper(person)

    # Primary email should be the first work email
    assert result["attributes"]["emails"][0]["email"] == "primary@work.com"
    assert result["attributes"]["emails"][0]["category"] == "work"

    # Primary phone should be the first work number
    assert result["attributes"]["phone_numbers"][0]["phone"] == "+1234567890"
    assert result["attributes"]["phone_numbers"][0]["category"] == "work"

def test_transform_address(transformer):
    """Test transforming a person with address details."""
    data = {
        "id": 123,
        "name": "John Doe",
        "emails": [{"email": "john@example.com", "category": "work"}],
        "address": {
            "street": "123 Main St",
            "city": "San Francisco",
            "state": "CA",
            "postal_code": "94105",
            "country": "US"
        }
    }
    
    result = transformer.to_mcp(data)
    assert result["attributes"]["address"]["street"] == "123 Main St"
    assert result["attributes"]["address"]["city"] == "San Francisco"
    assert result["attributes"]["address"]["state"] == "CA"
    assert result["attributes"]["address"]["postal_code"] == "94105"
    assert result["attributes"]["address"]["country"] == "US"

def test_transform_social_url_validation(transformer):
    """Test validation of social media URLs."""
    data = {
        "id": 123,
        "name": "John Doe",
        "emails": [{"email": "john@example.com", "category": "work"}],
        "socials": [
            {"url": "not-a-url", "category": "linkedin"},  # Invalid URL
            {"url": "https://linkedin.com/in/johndoe", "category": "linkedin"}  # Valid URL
        ]
    }
    
    with pytest.raises(ValidationError):
        transformer.to_mcp(data)