"""Tests for the Company transformer."""
import pytest
from datetime import datetime
from pydantic import HttpUrl

from app.mapping.company import CompanyTransformer
from app.models.copper import Company, Address, EmailPhone, SocialProfile, CustomField

def test_transform_minimal_company():
    """Test transformation of company with minimal data."""
    transformer = CompanyTransformer(Company)
    input_data = {
        "name": "ACME Corp"
    }
    
    result = transformer.transform_to_mcp(input_data)
    
    assert result["type"] == "company"
    assert result["id"] is None
    assert result["attributes"]["name"] == "ACME Corp"
    assert result["attributes"]["phone"] is None
    assert result["attributes"]["website"] is None
    assert result["relationships"]["assignee"]["data"] is None
    assert result["meta"]["interaction_count"] == 0

def test_transform_full_company():
    """Test transformation of company with all fields populated."""
    transformer = CompanyTransformer(Company)
    input_data = {
        "id": 123,
        "name": "ACME Corporation",
        "industry": "Technology",
        "email_domain": "acme.com",
        "assignee_id": 456,
        "details": "Global technology company",
        "contact_type_id": 1,
        "phone_numbers": [
            {"phone": "+1-555-0123", "category": "work"},
            {"phone": "+1-555-4567", "category": "other"}
        ],
        "socials": [
            {"url": "https://linkedin.com/company/acme", "category": "linkedin"},
            {"url": "https://twitter.com/acme", "category": "twitter"}
        ],
        "websites": [
            "https://acme.com",
            "https://blog.acme.com"
        ],
        "tags": ["Enterprise", "Technology"],
        "custom_fields": [
            {"custom_field_definition_id": 1, "value": "Custom Value"}
        ],
        "date_created": "2024-01-01T00:00:00Z",
        "date_modified": "2024-01-02T00:00:00Z",
        "interaction_count": 5,
        "annual_revenue": 1000000.0,
        "employee_count": 500,
        "address": {
            "street": "123 Tech Ave",
            "city": "San Francisco",
            "state": "CA",
            "postal_code": "94105",
            "country": "USA"
        }
    }
    
    result = transformer.transform_to_mcp(input_data)
    
    # Check basic attributes
    assert result["type"] == "company"
    assert result["id"] == "123"
    assert result["attributes"]["name"] == "ACME Corporation"
    assert result["attributes"]["industry"] == "Technology"
    assert result["attributes"]["email_domain"] == "acme.com"
    
    # Check contact info
    assert result["attributes"]["phone"] == "+1-555-0123"
    assert result["attributes"]["website"].rstrip("/") == "https://acme.com"
    assert len(result["meta"]["additional_phones"]) == 1
    assert result["meta"]["additional_phones"][0]["phone"] == "+1-555-4567"
    assert len(result["meta"]["additional_websites"]) == 1
    assert "blog.acme.com" in result["meta"]["additional_websites"][0]
    
    # Check relationships
    assert result["relationships"]["assignee"]["data"]["id"] == "456"
    
    # Check address
    assert result["attributes"]["address"]["street"] == "123 Tech Ave"
    assert result["attributes"]["address"]["city"] == "San Francisco"
    assert result["attributes"]["address"]["state"] == "CA"
    
    # Check metadata
    assert result["meta"]["interaction_count"] == 5
    assert result["meta"]["contact_type_id"] == 1
    assert len(result["meta"]["social_profiles"]) == 2
    assert result["meta"]["custom_fields"]["1"] == "Custom Value"
    
    # Check company-specific fields
    assert result["attributes"]["annual_revenue"] == 1000000.0
    assert result["attributes"]["employee_count"] == 500

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

def test_transform_validation():
    """Test validation of company data."""
    transformer = CompanyTransformer(Company)
    
    # Test invalid email domain
    with pytest.raises(Exception):
        transformer.transform_to_mcp({
            "name": "ACME Corp",
            "email_domain": "invalid@domain"
        })
    
    # Test invalid revenue
    with pytest.raises(Exception):
        transformer.transform_to_mcp({
            "name": "ACME Corp",
            "annual_revenue": -1000
        })
    
    # Test invalid employee count
    with pytest.raises(Exception):
        transformer.transform_to_mcp({
            "name": "ACME Corp",
            "employee_count": -50
        }) 