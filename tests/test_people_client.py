"""Tests for the Copper People API client."""
import pytest
from unittest.mock import Mock

from app.copper.client_base import CopperBaseClient
from app.copper.entities.people import PeopleClient


@pytest.fixture
def mock_base_client():
    """Create a mock base client."""
    client = Mock(spec=CopperBaseClient)
    return client


@pytest.fixture
def client(mock_base_client):
    """Create a PeopleClient with a mock base client."""
    return PeopleClient(mock_base_client)


def test_list_people(client, mock_base_client):
    """Test listing people with pagination."""
    expected = [{'id': 1, 'name': 'Test Person'}]
    mock_base_client._get.return_value = expected
    
    result = client.list(page_size=10, page_number=2)
    
    mock_base_client._get.assert_called_once_with(
        'people',
        params={'page_size': 10, 'page': 2}
    )
    assert result == expected


def test_get_person(client, mock_base_client):
    """Test getting a single person."""
    expected = {'id': 1, 'name': 'Test Person'}
    mock_base_client._get.return_value = expected
    
    result = client.get(1)
    
    mock_base_client._get.assert_called_once_with('people/1')
    assert result == expected


def test_create_person(client, mock_base_client):
    """Test creating a person."""
    person_data = {'name': 'New Person', 'email': 'test@example.com'}
    expected = {**person_data, 'id': 1}
    mock_base_client._post.return_value = expected
    
    result = client.create(person_data)
    
    mock_base_client._post.assert_called_once_with('people', json=person_data)
    assert result == expected


def test_update_person(client, mock_base_client):
    """Test updating a person."""
    person_data = {'name': 'Updated Name'}
    expected = {'id': 1, **person_data}
    mock_base_client._put.return_value = expected
    
    result = client.update(1, person_data)
    
    mock_base_client._put.assert_called_once_with('people/1', json=person_data)
    assert result == expected


def test_delete_person(client, mock_base_client):
    """Test deleting a person."""
    expected = {'success': True}
    mock_base_client._delete.return_value = expected
    
    result = client.delete(1)
    
    mock_base_client._delete.assert_called_once_with('people/1')
    assert result == expected


def test_search_people(client, mock_base_client):
    """Test searching for people."""
    search_criteria = {'email': 'test@example.com'}
    expected = [{'id': 1, 'name': 'Test Person'}]
    mock_base_client._post.return_value = expected
    
    result = client.search(search_criteria)
    
    mock_base_client._post.assert_called_once_with('people/search', json=search_criteria)
    assert result == expected


def test_get_related(client, mock_base_client):
    """Test getting related entities."""
    expected = [{'id': 1, 'type': 'opportunity'}]
    mock_base_client._get.return_value = expected
    
    result = client.get_related(1, 'opportunities')
    
    mock_base_client._get.assert_called_once_with('people/1/related/opportunities')
    assert result == expected


def test_update_custom_fields(client, mock_base_client):
    """Test updating custom fields."""
    custom_fields = [{'custom_field_definition_id': 1, 'value': 'test'}]
    expected = {'id': 1, 'custom_fields': custom_fields}
    mock_base_client._put.return_value = expected
    
    result = client.update_custom_fields(1, custom_fields)
    
    mock_base_client._put.assert_called_once_with(
        'people/1/custom_fields',
        json={'custom_fields': custom_fields}
    )
    assert result == expected


def test_convert_lead(client, mock_base_client):
    """Test converting a lead to a person."""
    details = {'status': 'converted'}
    expected = {'id': 1, 'type': 'person'}
    mock_base_client._post.return_value = expected
    
    result = client.convert_lead(1, details)
    
    mock_base_client._post.assert_called_once_with('people/1/convert', json=details)
    assert result == expected 