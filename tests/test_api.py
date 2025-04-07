"""Tests for the FastAPI application."""
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from httpx import ASGITransport

from app.main import app, get_copper_client
from app.copper.client.base import CopperClient
from app.copper.client.people import PeopleClient
from app.copper.client.companies import CompaniesClient
from app.copper.client.opportunities import OpportunitiesClient
from app.copper.client.activities import ActivitiesClient

@pytest.fixture
def mock_copper_client():
    """Create a mock Copper client."""
    mock = MagicMock(spec=CopperClient)
    return mock

@pytest.mark.asyncio
async def test_health_check():
    """Test the health check endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "copper-mcp"

@pytest.mark.asyncio
async def test_search_endpoint(mock_copper_client):
    """Test the search endpoint."""
    # Set up mock responses
    mock_people = [{"id": 1, "name": "Test Person"}]
    mock_companies = [{"id": 2, "name": "Test Company"}]

    # Create mock entity clients
    mock_people_client = AsyncMock(spec=PeopleClient)
    mock_companies_client = AsyncMock(spec=CompaniesClient)
    mock_opportunities_client = AsyncMock(spec=OpportunitiesClient)
    mock_activities_client = AsyncMock(spec=ActivitiesClient)

    # Configure mock methods
    mock_people_client.search = AsyncMock(return_value=mock_people)
    mock_companies_client.search = AsyncMock(return_value=mock_companies)
    mock_opportunities_client.search = AsyncMock(return_value=[])
    mock_activities_client.search = AsyncMock(return_value=[])

    # Mock client creation
    with patch("app.main.PeopleClient", return_value=mock_people_client), \
         patch("app.main.CompaniesClient", return_value=mock_companies_client), \
         patch("app.main.OpportunitiesClient", return_value=mock_opportunities_client), \
         patch("app.main.ActivitiesClient", return_value=mock_activities_client), \
         patch("app.main.person_transformer") as mock_person_transformer, \
         patch("app.main.company_transformer") as mock_company_transformer:

        # Configure transformer responses
        mock_person_transformer.to_mcp.return_value = {
            "type": "person",
            "source": "copper",
            "source_id": "1",
            "name": "Test Person"
        }
        mock_company_transformer.to_mcp.return_value = {
            "type": "company",
            "source": "copper",
            "source_id": "2",
            "name": "Test Company"
        }

        # Mock the get_copper_client dependency
        async def mock_get_copper_client():
            return mock_copper_client

        app.dependency_overrides[get_copper_client] = mock_get_copper_client

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/search?query=test")
            assert response.status_code == 200
            data = response.json()

            # Verify we got results from both people and companies
            assert len(data) == 2
            assert data[0]["type"] == "person"
            assert data[1]["type"] == "company"

            # Verify mock methods were called
            mock_people_client.search.assert_called_once_with({"query": "test"})
            mock_companies_client.search.assert_called_once_with({"query": "test"})

@pytest.mark.asyncio
async def test_get_person(mock_copper_client):
    """Test getting a person by ID."""
    mock_person = {
        "id": 1,
        "name": "Test Person",
        "emails": [{"email": "test@example.com"}]
    }

    # Create mock people client
    mock_people_client = AsyncMock(spec=PeopleClient)
    mock_people_client.get = AsyncMock(return_value=mock_person)

    # Mock client creation
    with patch("app.main.PeopleClient", return_value=mock_people_client), \
         patch("app.main.person_transformer") as mock_person_transformer:

        mock_person_transformer.to_mcp.return_value = {
            "type": "person",
            "source": "copper",
            "source_id": "1",
            "name": "Test Person",
            "email": "test@example.com"
        }

        # Mock the get_copper_client dependency
        async def mock_get_copper_client():
            return mock_copper_client

        app.dependency_overrides[get_copper_client] = mock_get_copper_client

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/people/1")
            assert response.status_code == 200
            data = response.json()
            assert data["type"] == "person"
            assert data["source"] == "copper"
            assert data["source_id"] == "1"

            # Verify mock methods were called
            mock_people_client.get.assert_called_once_with(1)

@pytest.mark.asyncio
async def test_get_company(mock_copper_client):
    """Test getting a company by ID."""
    mock_company = {
        "id": 1,
        "name": "Test Company",
        "email_domain": "example.com"
    }

    # Create mock companies client
    mock_companies_client = AsyncMock(spec=CompaniesClient)
    mock_companies_client.get = AsyncMock(return_value=mock_company)

    # Mock client creation
    with patch("app.main.CompaniesClient", return_value=mock_companies_client), \
         patch("app.main.company_transformer") as mock_company_transformer:

        mock_company_transformer.to_mcp.return_value = {
            "type": "company",
            "source": "copper",
            "source_id": "1",
            "name": "Test Company",
            "domain": "example.com"
        }

        # Mock the get_copper_client dependency
        async def mock_get_copper_client():
            return mock_copper_client

        app.dependency_overrides[get_copper_client] = mock_get_copper_client

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/companies/1")
            assert response.status_code == 200
            data = response.json()
            assert data["type"] == "company"
            assert data["source"] == "copper"
            assert data["source_id"] == "1"

            # Verify mock methods were called
            mock_companies_client.get.assert_called_once_with(1)

@pytest.mark.asyncio
async def test_error_handling(mock_copper_client):
    """Test error handling in the API."""
    # Create mock people client
    mock_people_client = AsyncMock(spec=PeopleClient)

    # Mock client creation
    with patch("app.main.PeopleClient", return_value=mock_people_client):
        # Mock the get_copper_client dependency for 404 error
        async def mock_get_copper_client_404():
            return mock_copper_client

        app.dependency_overrides[get_copper_client] = mock_get_copper_client_404

        # Test 404 error
        mock_people_client.get = AsyncMock(side_effect=Exception("Not found"))
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/people/999")
            assert response.status_code == 404
            data = response.json()
            assert "detail" in data

        # Test authentication error
        with patch("app.copper.auth.get_auth_token", side_effect=ValueError("Invalid token")):
            # Use the real get_copper_client function for auth error
            app.dependency_overrides[get_copper_client] = get_copper_client

            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                response = await ac.get("/people/1")
                assert response.status_code == 401
                data = response.json()
                assert "detail" in data 