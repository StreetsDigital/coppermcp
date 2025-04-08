"""Tests for the Copper API client."""
import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException

from app.copper.client.base import CopperClient


@pytest.fixture
def mock_session():
    """Create a mock requests.Session."""
    with patch('aiohttp.ClientSession') as mock:
        session = Mock()
        mock.return_value = session
        yield session


@pytest.fixture
def client(mock_session):
    """Create a client with mock session."""
    return CopperClient(
        api_user="test@example.com",
        api_password="test_password",
        user_id="12345"
    )


@pytest.mark.asyncio
async def test_get_request_success(client, mock_session):
    """Test successful GET request."""
    mock_response = Mock()
    mock_response.status = 200
    mock_response.content_type = "application/json"
    mock_response.json = Mock()
    mock_response.json.return_value = {'data': 'test'}
    mock_session.request.return_value.__aenter__.return_value = mock_response
    
    result = await client.get('test/endpoint', params={'key': 'value'})
    
    mock_session.request.assert_called_once()
    assert result == {'data': 'test'}


@pytest.mark.asyncio
async def test_post_request_success(client, mock_session):
    """Test successful POST request."""
    mock_response = Mock()
    mock_response.status = 200
    mock_response.content_type = "application/json"
    mock_response.json = Mock()
    mock_response.json.return_value = {'data': 'test'}
    mock_session.request.return_value.__aenter__.return_value = mock_response
    
    result = await client.post('test/endpoint', json={'key': 'value'})
    
    mock_session.request.assert_called_once()
    assert result == {'data': 'test'}


@pytest.mark.asyncio
async def test_put_request_success(client, mock_session):
    """Test successful PUT request."""
    mock_response = Mock()
    mock_response.status = 200
    mock_response.content_type = "application/json"
    mock_response.json = Mock()
    mock_response.json.return_value = {'data': 'test'}
    mock_session.request.return_value.__aenter__.return_value = mock_response
    
    result = await client.put('test/endpoint', json={'key': 'value'})
    
    mock_session.request.assert_called_once()
    assert result == {'data': 'test'}


@pytest.mark.asyncio
async def test_delete_request_success(client, mock_session):
    """Test successful DELETE request."""
    mock_response = Mock()
    mock_response.status = 200
    mock_response.content_type = "application/json"
    mock_response.json = Mock()
    mock_response.json.return_value = {'data': 'test'}
    mock_session.request.return_value.__aenter__.return_value = mock_response
    
    result = await client.delete('test/endpoint')
    
    mock_session.request.assert_called_once()
    assert result == {'data': 'test'}


@pytest.mark.asyncio
@pytest.mark.parametrize('status_code,expected_code', [
    (401, 401),
    (403, 403),
    (404, 404),
    (429, 429),
    (500, 502),
])
async def test_error_responses(client, mock_session, status_code, expected_code):
    """Test error response handling."""
    mock_response = Mock()
    mock_response.status = status_code
    mock_response.content_type = "application/json"
    mock_response.json = Mock()
    mock_response.json.return_value = {'message': 'error'}
    mock_session.request.return_value.__aenter__.return_value = mock_response
    
    with pytest.raises(CopperAPIError) as exc:
        await client.get('test/endpoint')
    
    assert exc.value.status_code == status_code 