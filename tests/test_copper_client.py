"""Tests for the Copper API client."""
import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException

from app.copper.client_base import CopperBaseClient


@pytest.fixture
def mock_session():
    """Create a mock requests.Session."""
    with patch('requests.Session') as mock:
        session = Mock()
        mock.return_value = session
        yield session


@pytest.fixture
def client(mock_session):
    """Create a CopperBaseClient with a mock session."""
    return CopperBaseClient()


def test_client_initialization(client, mock_session):
    """Test client initialization sets up headers correctly."""
    assert mock_session.headers.update.called
    headers = mock_session.headers.update.call_args[0][0]
    assert 'X-PW-AccessToken' in headers
    assert 'X-PW-Application' in headers
    assert 'X-PW-UserEmail' in headers
    assert headers['Content-Type'] == 'application/json'


def test_get_request_success(client, mock_session):
    """Test successful GET request."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'data': 'test'}
    mock_session.get.return_value = mock_response
    
    result = client._get('test/endpoint', params={'key': 'value'})
    
    mock_session.get.assert_called_once()
    assert result == {'data': 'test'}


def test_post_request_success(client, mock_session):
    """Test successful POST request."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'data': 'test'}
    mock_session.post.return_value = mock_response
    
    result = client._post('test/endpoint', json={'key': 'value'})
    
    mock_session.post.assert_called_once()
    assert result == {'data': 'test'}


def test_put_request_success(client, mock_session):
    """Test successful PUT request."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'data': 'test'}
    mock_session.put.return_value = mock_response
    
    result = client._put('test/endpoint', json={'key': 'value'})
    
    mock_session.put.assert_called_once()
    assert result == {'data': 'test'}


def test_delete_request_success(client, mock_session):
    """Test successful DELETE request."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'data': 'test'}
    mock_session.delete.return_value = mock_response
    
    result = client._delete('test/endpoint')
    
    mock_session.delete.assert_called_once()
    assert result == {'data': 'test'}


@pytest.mark.parametrize('status_code,expected_code', [
    (401, 401),
    (403, 403),
    (404, 404),
    (429, 429),
    (500, 502),
])
def test_error_responses(client, mock_session, status_code, expected_code):
    """Test error response handling."""
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.json.return_value = {'message': 'error'}
    mock_session.get.return_value = mock_response
    
    with pytest.raises(HTTPException) as exc:
        client._get('test/endpoint')
    
    assert exc.value.status_code == expected_code 