"""Tests for the main FastAPI application."""
from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    """Test the health check endpoint returns expected response.
    
    Args:
        client: Test client fixture
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "copper-mcp"
    assert "version" in data


def test_http_exception_handler(client: TestClient) -> None:
    """Test the HTTP exception handler formats errors correctly.
    
    Args:
        client: Test client fixture
    """
    response = client.get("/test-error")
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == 400
    assert data["error"]["message"] == "Test error"


def test_general_exception_handler(client: TestClient) -> None:
    """Test the general exception handler handles unexpected errors.
    
    Args:
        client: Test client fixture
    """
    response = client.get("/test-unexpected-error")
    assert response.status_code == 500
    data = response.json()
    assert data["error"]["code"] == 500
    assert data["error"]["message"] == "Internal server error" 