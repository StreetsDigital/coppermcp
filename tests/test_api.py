from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch, MagicMock
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from typing import Dict, Any, Optional
import asyncio

from app.main import app, get_copper_client
from app.copper.client import CopperClient
from app.copper.client.base import CopperAPIError
from app.copper.auth import AuthenticationError
from app.models.copper import Person, Company, Opportunity, Activity, EmailPhone, ActivityType, ParentEntity, Social, CustomField, Address
import os

# Create a fixed timestamp for testing
NOW = datetime.now(timezone.utc)

# Mock data constants
MOCK_PERSON = {
    "id": 1,
    "name": "Test Person",
    "first_name": "Test",
    "last_name": "Person",
    "title": "Developer",
    "company_name": "Test Company",
    "company_id": 1,
    "emails": [{"category": "work", "email": "test@example.com"}],
    "phone_numbers": [{"category": "work", "phone": "1234567890"}],
    "socials": [],
    "websites": ["https://example.com"],
    "address": {
        "street": "123 Test St",
        "city": "Test City",
        "state": "TS",
        "postal_code": "12345",
        "country": "Test Country"
    },
    "assignee_id": 1,
    "contact_type_id": 1,
    "details": "Test person details",
    "tags": ["test"],
    "custom_fields": [],
    "date_created": NOW,
    "date_modified": NOW,
    "interaction_count": 0
}

MOCK_COMPANY = {
    "id": 1,
    "name": "Test Company",
    "assignee_id": 1,
    "address": {
        "street": "123 Test St",
        "city": "Test City",
        "state": "TS",
        "postal_code": "12345",
        "country": "Test Country"
    },
    "phone_numbers": [{"category": "work", "phone": "1234567890"}],
    "websites": ["https://example.com"],
    "email_domain": "example.com",
    "details": "Test company details",
    "tags": ["test"],
    "custom_fields": [],
    "industry": "Technology",
    "annual_revenue": 1000000,
    "employee_count": 100,
    "date_created": NOW,
    "date_modified": NOW,
    "interaction_count": 0
}

MOCK_OPPORTUNITY = {
    "id": 1,
    "name": "Test Opportunity",
    "assignee_id": 1,
    "company_id": 1,
    "company_name": "Test Company",
    "primary_contact_id": 1,
    "status": "Open",
    "priority": "High",
    "pipeline_id": 1,
    "pipeline_stage_id": 1,
    "monetary_value": 1000,
    "win_probability": 50,
    "close_date": NOW,
    "details": "Test opportunity details",
    "tags": ["test"],
    "custom_fields": [],
    "date_created": NOW,
    "date_modified": NOW,
    "interaction_count": 0
}

MOCK_ACTIVITY = {
    "id": 1,
    "type": {"category": "note", "id": 1},
    "details": "Test activity",
    "activity_date": int(NOW.timestamp()),
    "parent": {"type": "person", "id": 1},
    "user_id": 1,
    "assignee_id": 1,
    "custom_fields": [],
    "date_created": NOW,
    "date_modified": NOW,
    "tags": ["test"]
}

# Create test client
client = TestClient(app)

@pytest_asyncio.fixture
async def mock_copper_client():
    """Create a mock Copper client for testing."""
    mock_client = AsyncMock(spec=CopperClient)
    mock_client.auth_token = "test_token"  # Add auth token
    mock_client.session = AsyncMock()  # Add session

    # Mock base client methods
    async def mock_get(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Mock GET request."""
        await asyncio.sleep(0)  # Simulate async behavior
        if endpoint == "/people/1":
            return Person.model_validate(MOCK_PERSON)
        elif endpoint == "/companies/1":
            return Company.model_validate(MOCK_COMPANY)
        elif endpoint == "/opportunities/1":
            return Opportunity.model_validate(MOCK_OPPORTUNITY)
        elif endpoint == "/activities/1":
            return Activity.model_validate(MOCK_ACTIVITY)
        elif endpoint == "/people/search":
            return [Person.model_validate(MOCK_PERSON)]
        elif endpoint == "/companies/search":
            return [Company.model_validate(MOCK_COMPANY)]
        elif endpoint == "/opportunities/search":
            return [Opportunity.model_validate(MOCK_OPPORTUNITY)]
        elif endpoint == "/activities/search":
            return [Activity.model_validate(MOCK_ACTIVITY)]
        elif endpoint == "/people/999":
            raise CopperAPIError("404 Not Found")
        elif endpoint == "/people/401":
            raise AuthenticationError("Invalid token")
        elif endpoint == "/people/502":
            raise CopperAPIError("502 Bad Gateway")
        else:
            raise CopperAPIError("404 Not Found")  # Default to 404 for unknown endpoints

    async def mock_post(endpoint: str, json: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Mock POST request."""
        await asyncio.sleep(0)  # Simulate async behavior
        if endpoint == "/people/search":
            return [Person.model_validate(MOCK_PERSON)]
        elif endpoint == "/companies/search":
            return [Company.model_validate(MOCK_COMPANY)]
        elif endpoint == "/opportunities/search":
            return [Opportunity.model_validate(MOCK_OPPORTUNITY)]
        elif endpoint == "/activities/search":
            return [Activity.model_validate(MOCK_ACTIVITY)]
        else:
            return []

    async def mock_ensure_session():
        """Mock session management."""
        await asyncio.sleep(0)  # Simulate async behavior
        return None

    async def mock_close():
        """Mock session cleanup."""
        await asyncio.sleep(0)  # Simulate async behavior
        return None

    mock_client.get = AsyncMock(side_effect=mock_get)
    mock_client.post = AsyncMock(side_effect=mock_post)
    mock_client._ensure_session = AsyncMock(side_effect=mock_ensure_session)
    mock_client.close = AsyncMock(side_effect=mock_close)

    # Mock entity client methods
    mock_client.people = AsyncMock()
    mock_client.people.get = AsyncMock(side_effect=mock_get)
    mock_client.people.search = AsyncMock(side_effect=mock_post)
    mock_client.people.client = mock_client  # Add base client reference

    mock_client.companies = AsyncMock()
    mock_client.companies.get = AsyncMock(side_effect=mock_get)
    mock_client.companies.search = AsyncMock(side_effect=mock_post)
    mock_client.companies.client = mock_client  # Add base client reference

    mock_client.opportunities = AsyncMock()
    mock_client.opportunities.get = AsyncMock(side_effect=mock_get)
    mock_client.opportunities.search = AsyncMock(side_effect=mock_post)
    mock_client.opportunities.client = mock_client  # Add base client reference

    mock_client.activities = AsyncMock()
    mock_client.activities.get = AsyncMock(side_effect=mock_get)
    mock_client.activities.search = AsyncMock(side_effect=mock_post)
    mock_client.activities.client = mock_client  # Add base client reference

    # Override dependency
    app.dependency_overrides[get_copper_client] = lambda: mock_client

    yield mock_client

    # Clear dependency overrides
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "copper-mcp",
        "version": "0.1.0"
    }

@pytest.mark.asyncio
async def test_search_all_entities(mock_copper_client):
    """Test search across all entity types."""
    response = client.get("/search?query=test")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 4  # One of each entity type

@pytest.mark.asyncio
async def test_search_filtered_by_type(mock_copper_client):
    """Test search filtered by entity type."""
    response = client.get("/search?query=test&entity_type=person")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1

@pytest.mark.asyncio
async def test_get_person(mock_copper_client):
    """Test get person endpoint."""
    response = client.get("/people/1")
    assert response.status_code == 200
    assert response.json()["type"] == "person"

@pytest.mark.asyncio
async def test_get_company(mock_copper_client):
    """Test get company endpoint."""
    response = client.get("/companies/1")
    assert response.status_code == 200
    assert response.json()["type"] == "company"

@pytest.mark.asyncio
async def test_get_opportunity(mock_copper_client):
    """Test get opportunity endpoint."""
    response = client.get("/opportunities/1")
    assert response.status_code == 200
    assert response.json()["type"] == "opportunity"

@pytest.mark.asyncio
async def test_get_activity(mock_copper_client):
    """Test get activity endpoint."""
    response = client.get("/activities/1")
    assert response.status_code == 200
    assert response.json()["type"] == "activity"

@pytest.mark.asyncio
async def test_not_found_error(mock_copper_client):
    """Test 404 error handling."""
    response = client.get("/people/999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_authentication_error():
    """Test authentication error handling."""
    app.dependency_overrides.clear()  # Clear previous override
    with patch("app.copper.auth.get_auth_token") as mock:
        mock.side_effect = AuthenticationError("Invalid token")
        response = client.get("/people/1")
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_copper_api_error(mock_copper_client):
    """Test Copper API error handling."""
    mock_copper_client.get = AsyncMock(side_effect=CopperAPIError("API Error"))
    response = client.get("/people/1")
    assert response.status_code == 502

@pytest.mark.asyncio
async def test_validation_error(mock_copper_client):
    """Test validation error handling."""
    mock_copper_client.get = AsyncMock(return_value={"invalid": "data"})  # Invalid person data
    response = client.get("/people/1")
    assert response.status_code == 422