"""Tests for the Copper People API client."""
import pytest
from unittest.mock import Mock

from app.copper.client.base import CopperClient
from app.copper.client.people import PeopleClient
from app.models.copper import Person, PersonCreate, PersonUpdate


@pytest.fixture
def mock_base_client():
    """Create a mock base client."""
    return Mock(spec=CopperClient)


@pytest.fixture
def client(mock_base_client):
    """Create a people client with mock base client."""
    return PeopleClient(mock_base_client)


def test_list_people(client, mock_base_client):
    """Test listing people with pagination."""
    expected = [
        {
            "id": 1,
            "name": "Test Person",
            "email": "test@example.com",
            "phone_numbers": [{"number": "123-456-7890", "category": "work"}],
            "socials": [],
            "websites": []
        }
    ]
    mock_base_client._get.return_value = expected
    
    result = client.list(page_size=10, page_number=2)
    assert len(result) == 1
    assert isinstance(result[0], Person)
    assert result[0].id == 1
    assert result[0].name == "Test Person"
    assert result[0].email == "test@example.com"


def test_get_person(client, mock_base_client):
    """Test getting a single person."""
    expected = {
        "id": 1,
        "name": "Test Person",
        "email": "test@example.com",
        "phone_numbers": [{"number": "123-456-7890", "category": "work"}],
        "socials": [],
        "websites": []
    }
    mock_base_client._get.return_value = expected
    
    result = client.get(1)
    assert isinstance(result, Person)
    assert result.id == 1
    assert result.name == "Test Person"
    assert result.email == "test@example.com"


def test_create_person(client, mock_base_client):
    """Test creating a person."""
    person_data = PersonCreate(
        name="New Person",
        email="test@example.com",
        phone_numbers=[{"number": "123-456-7890", "category": "work"}]
    )
    expected = {
        "id": 1,
        "name": "New Person",
        "email": "test@example.com",
        "phone_numbers": [{"number": "123-456-7890", "category": "work"}],
        "socials": [],
        "websites": []
    }
    mock_base_client._post.return_value = expected
    
    result = client.create(person_data)
    assert isinstance(result, Person)
    assert result.id == 1
    assert result.name == "New Person"
    assert result.email == "test@example.com"


def test_update_person(client, mock_base_client):
    """Test updating a person."""
    person_data = PersonUpdate(
        name="Updated Name",
        email="updated@example.com"
    )
    expected = {
        "id": 1,
        "name": "Updated Name",
        "email": "updated@example.com",
        "phone_numbers": [],
        "socials": [],
        "websites": []
    }
    mock_base_client._put.return_value = expected
    
    result = client.update(1, person_data)
    assert isinstance(result, Person)
    assert result.id == 1
    assert result.name == "Updated Name"
    assert result.email == "updated@example.com"


def test_delete_person(client, mock_base_client):
    """Test deleting a person."""
    mock_base_client._delete.return_value = None
    
    result = client.delete(1)
    assert result is None
    mock_base_client._delete.assert_called_once_with("/people/1")


def test_search_people(client, mock_base_client):
    """Test searching for people."""
    expected = [
        {
            "id": 1,
            "name": "Test Person",
            "email": "test@example.com",
            "phone_numbers": [{"number": "123-456-7890", "category": "work"}],
            "socials": [],
            "websites": []
        }
    ]
    mock_base_client._post.return_value = expected
    
    result = client.search({"name": "Test"})
    assert len(result) == 1
    assert isinstance(result[0], Person)
    assert result[0].id == 1
    assert result[0].name == "Test Person"
    assert result[0].email == "test@example.com"


def test_update_custom_fields(client, mock_base_client):
    """Test updating custom fields."""
    custom_fields = [{"custom_field_definition_id": 1, "value": "test"}]
    expected = {
        "id": 1,
        "name": "Test Person",
        "email": "test@example.com",
        "phone_numbers": [],
        "socials": [],
        "websites": [],
        "custom_fields": custom_fields
    }
    mock_base_client._put.return_value = expected
    
    result = client.update_custom_fields(1, custom_fields)
    assert isinstance(result, Person)
    assert result.id == 1
    assert result.custom_fields == custom_fields


def test_convert_lead(client, mock_base_client):
    """Test converting a lead to a person."""
    details = {"status": "converted"}
    expected = {
        "id": 1,
        "name": "Test Person",
        "email": "test@example.com",
        "phone_numbers": [],
        "socials": [],
        "websites": [],
        "type": "person"
    }
    mock_base_client._post.return_value = expected
    
    result = client.convert_lead(1, details)
    assert isinstance(result, Person)
    assert result.id == 1
    assert result.name == "Test Person"
    assert result.email == "test@example.com"


def test_get_related(client, mock_base_client):
    """Test getting related entities."""
    expected = [{'id': 1, 'type': 'opportunity'}]
    mock_base_client._get.return_value = expected
    
    result = client.get_related(1, 'opportunities')
    
    mock_base_client._get.assert_called_once_with('people/1/related/opportunities')
    assert result == expected 