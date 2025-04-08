"""Tests for company data transformation."""
import pytest
from datetime import datetime, timezone
from pydantic import HttpUrl

from app.mapping.company import CompanyTransformer
from app.models.copper import Company as CopperCompany
from app.models.mcp import MCPCompany
from app.models.copper import EmailPhone, Social, Address, CustomField

@pytest.fixture
def transformer():
    """Create a company transformer instance."""
    return CompanyTransformer(CopperCompany, MCPCompany)

@pytest.fixture
def mock_copper_company():
    """Create a mock Copper company with full data."""
    return {
        "id": "12345",
        "name": "Test Company",
        "email_domain": "test.com",
        "details": "Test company details",
        "industry": "Technology",
        "annual_revenue": 1000000,
        "employee_count": 50,
        "status": "active",
        "phone_numbers": [
            {"phone": "123-456-7890", "category": "work"},
            {"phone": "098-765-4321", "category": "mobile"}
        ],
        "socials": [
            {"url": "https://linkedin.com/company/test", "category": "linkedin"},
            {"url": "https://twitter.com/test", "category": "twitter"}
        ],
        "websites": ["https://test.com", "https://blog.test.com"],
        "address": {
            "street": "123 Test St",
            "city": "Test City",
            "state": "TS",
            "postal_code": "12345",
            "country": "Test Country"
        },
        "assignee_id": "98765",
        "primary_contact_id": "54321",
        "tags": ["tech", "enterprise"],
        "custom_fields": [
            {"custom_field_definition_id": "cf_1", "value": "Test Value"}
        ],
        "interaction_count": 10,
        "date_created": int(datetime(2023, 1, 1, tzinfo=timezone.utc).timestamp()),
        "date_modified": int(datetime(2023, 1, 2, tzinfo=timezone.utc).timestamp())
    }

def test_transform_full_company(transformer, mock_copper_company):
    """Test transformation of a company with all fields populated."""
    company = CopperCompany(**mock_copper_company)
    result = transformer._to_mcp_format(company)
    
    assert result["type"] == "company"
    assert result["attributes"]["name"] == "Test Company"
    assert result["attributes"]["email_domain"] == "test.com"
    assert result["attributes"]["industry"] == "Technology"
    assert result["attributes"]["annual_revenue"] == 1000000
    assert result["attributes"]["employee_count"] == 50
    assert result["attributes"]["status"] == "active"
    assert result["attributes"]["phone"] == "123-456-7890"  # Primary (work) phone
    assert result["attributes"]["website"] == "https://test.com"  # Primary website
    
    # Check contact methods
    assert len(result["attributes"]["phone_numbers"]) == 2
    assert result["attributes"]["phone_numbers"][0]["number"] == "123-456-7890"
    assert len(result["attributes"]["socials"]) == 2
    assert "linkedin.com" in result["attributes"]["socials"][0]["url"]
    assert len(result["attributes"]["websites"]) == 2
    
    # Check address
    assert result["attributes"]["address"]["street"] == "123 Test St"
    assert result["attributes"]["address"]["city"] == "Test City"
    
    # Check relationships
    assert result["relationships"]["assignee"]["data"]["id"] == "98765"
    assert result["relationships"]["primary_contact"]["data"]["id"] == "54321"
    
    # Check meta
    assert result["meta"]["interaction_count"] == 10
    assert result["meta"]["created_at"] == "2023-01-01T00:00:00Z"
    assert result["meta"]["updated_at"] == "2023-01-02T00:00:00Z"

def test_transform_minimal_company(transformer):
    """Test transformation of a company with minimal required fields."""
    minimal_data = {
        "name": "Minimal Company",
        "email_domain": "minimal.com"
    }
    company = CopperCompany(**minimal_data)
    result = transformer._to_mcp_format(company)
    
    assert result["type"] == "company"
    assert result["attributes"]["name"] == "Minimal Company"
    assert result["attributes"]["email_domain"] == "minimal.com"
    assert result["attributes"]["phone"] is None
    assert result["attributes"]["website"] is None
    assert result["attributes"]["address"] is None
    assert not result["relationships"]
    assert result["meta"]["interaction_count"] == 0

def test_transform_empty_custom_fields(transformer, mock_copper_company):
    """Test transformation of a company with empty custom fields."""
    company_data = mock_copper_company.copy()
    company_data["custom_fields"] = []
    company = CopperCompany(**company_data)
    result = transformer._to_mcp_format(company)
    
    assert isinstance(result, dict)
    assert result["meta"]["custom_fields"] == []

def test_transform_validation(transformer):
    """Test validation of required fields."""
    with pytest.raises(ValueError):
        transformer._to_mcp_format(CopperCompany())

def test_transform_primary_contact_methods(transformer, mock_copper_company):
    """Test extraction of primary contact methods."""
    # Test work phone priority
    company = CopperCompany(**mock_copper_company)
    result = transformer._to_mcp_format(company)
    assert result["attributes"]["phone"] == "123-456-7890"  # Work phone
    
    # Test fallback to first phone when no work phone
    company_data = mock_copper_company.copy()
    company_data["phone_numbers"] = [
        {"phone": "555-555-5555", "category": "mobile"},
        {"phone": "444-444-4444", "category": "other"}
    ]
    company = CopperCompany(**company_data)
    result = transformer._to_mcp_format(company)
    assert result["attributes"]["phone"] == "555-555-5555"  # First available

def test_transform_reverse(transformer, mock_copper_company):
    """Test reverse transformation from MCP to Copper format."""
    # First transform to MCP
    company = CopperCompany(**mock_copper_company)
    mcp_data = transformer._to_mcp_format(company)
    mcp_company = MCPCompany(**mcp_data)
    
    # Then transform back to Copper
    result = transformer._to_copper_format(mcp_company)
    
    assert result["name"] == mock_copper_company["name"]
    assert result["email_domain"] == mock_copper_company["email_domain"]
    assert result["industry"] == mock_copper_company["industry"]
    assert result["annual_revenue"] == mock_copper_company["annual_revenue"]
    assert result["employee_count"] == mock_copper_company["employee_count"]
    assert result["assignee_id"] == int(mock_copper_company["assignee_id"])
    assert result["primary_contact_id"] == int(mock_copper_company["primary_contact_id"])
    assert isinstance(result["address"], dict)
    assert result["address"]["street"] == mock_copper_company["address"]["street"] 