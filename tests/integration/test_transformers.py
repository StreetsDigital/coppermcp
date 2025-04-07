"""Integration tests for data transformers.

These tests verify that our transformers correctly handle real Copper API data
and produce valid MCP format output.
"""
import pytest
from typing import Dict, Any

from app.copper.client.people import PeopleClient
from app.copper.client.companies import CompaniesClient
from app.copper.client.activities import ActivitiesClient
from app.mapping.person import PersonTransformer
from app.mapping.company import CompanyTransformer
from app.mapping.activity import ActivityTransformer
from app.copper.models.people import Person
from app.copper.models.companies import Company
from app.copper.models.activities import Activity


@pytest.fixture
async def people_client(copper_client):
    """Fixture for PeopleClient."""
    return PeopleClient(copper_client)


@pytest.fixture
async def companies_client(copper_client):
    """Fixture for CompaniesClient."""
    return CompaniesClient(copper_client)


@pytest.fixture
async def activities_client(copper_client):
    """Fixture for ActivitiesClient."""
    return ActivitiesClient(copper_client)


def validate_mcp_format(data: Dict[str, Any]) -> None:
    """Validate that data follows MCP format requirements.
    
    Args:
        data: The transformed data to validate
        
    Raises:
        AssertionError: If data doesn't match MCP format
    """
    assert isinstance(data, dict)
    assert "type" in data
    assert isinstance(data["type"], str)
    
    if "id" in data:
        assert isinstance(data["id"], str)
    
    assert "attributes" in data
    assert isinstance(data["attributes"], dict)
    
    assert "relationships" in data
    assert isinstance(data["relationships"], dict)
    
    assert "meta" in data
    assert isinstance(data["meta"], dict)
    
    # Verify timestamps are in ISO8601 format with Z timezone
    for attr in ["created_at", "updated_at"]:
        if attr in data["attributes"]:
            assert data["attributes"][attr] is None or (
                isinstance(data["attributes"][attr], str) and
                data["attributes"][attr].endswith("Z")
            )


@pytest.mark.asyncio
async def test_person_transformer_with_api_data(people_client):
    """Test PersonTransformer with real API data."""
    # Get a real person from the API
    people = await people_client.search(page_size=1)
    assert people, "No people found in Copper"
    
    person_data = people[0]
    transformer = PersonTransformer(Person)
    result = transformer.transform_to_mcp(person_data)
    
    # Validate MCP format
    validate_mcp_format(result)
    
    # Verify person-specific fields
    assert result["type"] == "person"
    assert "email" in result["attributes"]
    assert "name" in result["attributes"]
    if result["attributes"].get("email"):
        assert "@" in result["attributes"]["email"]


@pytest.mark.asyncio
async def test_company_transformer_with_api_data(companies_client):
    """Test CompanyTransformer with real API data."""
    # Get a real company from the API
    companies = await companies_client.search(page_size=1)
    assert companies, "No companies found in Copper"
    
    company_data = companies[0]
    transformer = CompanyTransformer(Company)
    result = transformer.transform_to_mcp(company_data)
    
    # Validate MCP format
    validate_mcp_format(result)
    
    # Verify company-specific fields
    assert result["type"] == "company"
    assert "name" in result["attributes"]
    if result["attributes"].get("website"):
        assert "://" in result["attributes"]["website"]


@pytest.mark.asyncio
async def test_activity_transformer_with_api_data(activities_client):
    """Test ActivityTransformer with real API data."""
    # Get a real activity from the API
    activities = await activities_client.search(page_size=1)
    assert activities, "No activities found in Copper"
    
    activity_data = activities[0]
    transformer = ActivityTransformer(Activity)
    result = transformer.transform_to_mcp(activity_data)
    
    # Validate MCP format
    validate_mcp_format(result)
    
    # Verify activity-specific fields
    assert result["type"] == "activity"
    assert "activity_type" in result["attributes"]
    assert "details" in result["attributes"]
    assert result["relationships"]["parent"]["data"]["type"] in ["person", "company", "opportunity"]


@pytest.mark.asyncio
async def test_transformer_error_handling(people_client):
    """Test transformer error handling with invalid data."""
    # Get a real person but corrupt the data
    people = await people_client.search(page_size=1)
    assert people, "No people found in Copper"
    
    person_data = people[0]
    person_data["email_addresses"] = [{"email": "invalid-email"}]  # Missing category
    
    transformer = PersonTransformer(Person)
    with pytest.raises(Exception):  # Should raise validation error
        transformer.transform_to_mcp(person_data) 