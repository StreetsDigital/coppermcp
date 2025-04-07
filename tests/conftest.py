"""Pytest configuration and fixtures for the Copper MCP Server tests."""
import pytest
import pytest_asyncio
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.exceptions import ExceptionMiddleware
import os
import vcr
from typing import Generator

from app.copper.client.base import CopperClient
from app.copper.auth import get_auth_token
from app.copper.client.people import PeopleClient
from app.copper.client.companies import CompaniesClient
from app.copper.client.activities import ActivitiesClient

# Configure VCR
vcr_config = vcr.VCR(
    cassette_library_dir="tests/vcr_cassettes",
    record_mode="once",
    match_on=["method", "scheme", "host", "port", "path", "query", "body"],
    filter_headers=["authorization"],  # Don't record auth headers
    filter_post_data_parameters=["token", "email"],  # Don't record sensitive data
)

@pytest_asyncio.fixture
async def copper_client() -> CopperClient:
    """Create a CopperClient instance for testing.
    
    This fixture uses environment variables for authentication:
    - COPPER_API_TOKEN: Your Copper API token
    - COPPER_EMAIL: Your Copper email address
    
    Returns:
        CopperClient: A configured client for Copper API
    """
    token = os.getenv("COPPER_API_TOKEN")
    email = os.getenv("COPPER_EMAIL")
    
    if not token or not email:
        pytest.skip("Copper API credentials not found in environment")
    
    auth_token = get_auth_token(token, email)
    return CopperClient(auth_token)

@pytest_asyncio.fixture
async def people_client(copper_client: CopperClient) -> PeopleClient:
    """Fixture for PeopleClient."""
    return PeopleClient(copper_client)

@pytest_asyncio.fixture
async def companies_client(copper_client: CopperClient) -> CompaniesClient:
    """Fixture for CompaniesClient."""
    return CompaniesClient(copper_client)

@pytest_asyncio.fixture
async def activities_client(copper_client: CopperClient) -> ActivitiesClient:
    """Fixture for ActivitiesClient."""
    return ActivitiesClient(copper_client)

@pytest.fixture
def app() -> FastAPI:
    """Create a fresh FastAPI application for testing.
    
    Returns:
        FastAPI: A configured test application
    """
    app = FastAPI(
        title="Copper MCP Server Test",
        description="Test instance of Model Context Protocol implementation for Copper CRM",
        version="0.1.0"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add routes first
    @app.get("/health")
    async def health_check() -> dict:
        """Health check endpoint to verify service status."""
        return {
            "status": "healthy",
            "service": "copper-mcp",
            "version": "0.1.0"
        }
    
    @app.get("/test-error")
    async def test_error():
        raise HTTPException(status_code=400, detail="Test error")
        
    @app.get("/test-unexpected-error")
    async def test_unexpected_error():
        raise ValueError("Unexpected error")
    
    # Add exception handlers
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.status_code,
                    "message": str(exc.detail)
                }
            }
        )

    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        print(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": 500,
                    "message": "Internal server error"
                }
            }
        )
    
    # Register exception handlers
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    # Add exception middleware as the outermost layer
    app.add_middleware(
        ExceptionMiddleware,
        handlers=app.exception_handlers,
    )
    
    return app

@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Create a test client for the FastAPI application.
    
    Args:
        app: The FastAPI application fixture
    
    Returns:
        TestClient: A configured test client
    """
    return TestClient(app)

@pytest.fixture
def vcr_cassette(request) -> Generator[vcr.VCR, None, None]:
    """Provides a VCR instance for recording/replaying HTTP interactions."""
    # Use the test name as the cassette name
    cassette_name = request.node.name.replace("[", "_").replace("]", "_")
    with vcr_config.use_cassette(f"{cassette_name}.yaml"):
        yield vcr_config 