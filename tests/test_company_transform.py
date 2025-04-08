"""Tests for the Company transformer."""
import pytest
from datetime import datetime, timezone
from typing import Dict, Any
from pydantic import HttpUrl

from app.mapping.company import CompanyTransformer
from app.models.copper import Company, Address, EmailPhone, Social, CustomField
from app.models.mcp import MCPCompany

@pytest.fixture
def transformer():
    """Create a company transformer for testing."""
    return CompanyTransformer(copper_model=Company, mcp_model=MCPCompany)

def test_transform_minimal_company(transformer):
    """Test transforming a company with minimal data."""
    data = {
        "id": 123,
        "name": "Test Company",
        "email_domain": "test.com",
        "details": None,
        "phone_numbers": [],
        "socials": [],
        "websites": []
    }
    
    result = transformer.to_mcp(data)
    assert result["type"] == "company"
    assert result["source"] == "copper"
    assert result["source_id"] == "123"
    assert result["attributes"]["name"] == "Test Company"
    assert result["attributes"]["email_domain"] == "test.com"

def test_transform_full_company(transformer):
    """Test transforming a company with all fields populated."""
    now = int(datetime.now(timezone.utc).timestamp())
    data = {
        "id": 789,
        "name": "Full Company",
        "email_domain": "full.com",
        "details": "Company details",
        "phone_numbers": [{"number": "123-456-7890"}],
        "socials": [{"url": "https://linkedin.com/company/test"}],
        "websites": ["https://full.com"],
        "date_created": now,
        "date_modified": now,
        "assignee_id": 101,
        "custom_fields": [
            {"custom_field_definition_id": 201, "value": "Custom value"}
        ]
    }
    
    result = transformer.to_mcp(data)
    assert result["type"] == "company"
    assert result["source"] == "copper"
    assert result["source_id"] == "789"
    assert result["attributes"]["name"] == "Full Company"
    assert result["attributes"]["email_domain"] == "full.com"
    assert result["attributes"]["details"] == "Company details"
    assert result["attributes"]["phone_numbers"][0]["number"] == "123-456-7890"
    assert result["attributes"]["socials"][0]["url"] == "https://linkedin.com/company/test"
    assert result["attributes"]["websites"][0] == "https://full.com"
    assert result["meta"]["custom_fields"][0]["value"] == "Custom value"

def test_transform_validation(transformer):
    """Test validation of company data."""
    data = {
        "id": 123,
        "name": "",  # Invalid empty name
        "email_domain": "test.com",
        "details": None,
        "phone_numbers": [],
        "socials": [],
        "websites": []
    }
    
    with pytest.raises(ValueError):
        transformer.to_mcp(data)

def test_transform_empty_custom_fields(transformer):
    """Test transforming a company with empty custom fields."""
    data = {
        "id": 123,
        "name": "Test Company",
        "email_domain": "test.com",
        "details": None,
        "phone_numbers": [],
        "socials": [],
        "websites": [],
        "custom_fields": []
    }
    
    result = transformer.to_mcp(data)
    assert result["meta"]["custom_fields"] == []

def test_transform_work_phone_priority():
    """Test that work phone is prioritized."""
    transformer = CompanyTransformer(Company)
    input_data = {
        "name": "ACME Corp",
        "phone_numbers": [
            {"phone": "+1-555-1111", "category": "other"},
            {"phone": "+1-555-2222", "category": "work"},
        ]
    }
    
    result = transformer.transform_to_mcp(input_data)
    
    assert result["attributes"]["phone"] == "+1-555-2222"

def test_transform_empty_lists():
    """Test handling of empty contact lists."""
    transformer = CompanyTransformer(Company)
    input_data = {
        "name": "ACME Corp",
        "phone_numbers": [],
        "socials": [],
        "websites": [],
        "tags": [],
        "custom_fields": []
    }
    
    result = transformer.transform_to_mcp(input_data)
    
    assert result["attributes"]["phone"] is None
    assert result["attributes"]["website"] is None
    assert result["meta"]["additional_phones"] == []
    assert result["meta"]["social_profiles"] == []
    assert result["meta"]["additional_websites"] == []
    assert result["attributes"]["tags"] == []
    assert result["meta"]["custom_fields"] == {} 