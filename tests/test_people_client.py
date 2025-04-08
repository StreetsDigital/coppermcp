"""Tests for the Copper People API client."""
import pytest
from unittest.mock import Mock

from app.copper.client.base import CopperClient
from app.copper.client.people import PeopleClient
from app.models.copper import Person, PersonCreate, PersonUpdate, EmailPhone, Address, Social, CustomField


@pytest.fixture
def mock_base_client():
    """Create a mock base client."""
    return Mock(spec=CopperClient)


@pytest.fixture
def client(mock_base_client):
    """Create a people client with mock base client."""
    return PeopleClient(mock_base_client)


@pytest.fixture
def mock_person():
    """Create a mock person with all fields."""
    return {
        "id": "12345",
        "name": "John Doe",
        "emails": [
            {"email": "john@example.com", "category": "work"},
            {"email": "john.doe@personal.com", "category": "personal"}
        ],
        "phone_numbers": [
            {"number": "123-456-7890", "category": "work"},
            {"number": "098-765-4321", "category": "mobile"}
        ],
        "socials": [
            {"url": "https://linkedin.com/in/johndoe", "category": "linkedin"},
            {"url": "https://twitter.com/johndoe", "category": "twitter"}
        ],
        "websites": [
            {"url": "https://example.com", "category": "work"},
            {"url": "https://blog.example.com", "category": "blog"}
        ],
        "address": {
            "street": "123 Main St",
            "city": "San Francisco",
            "state": "CA",
            "postal_code": "94105",
            "country": "USA"
        },
        "assignee_id": "67890",
        "contact_type_id": "1",
        "details": "Test person details",
        "tags": ["test", "mock"],
        "custom_fields": [
            {"custom_field_definition_id": "1", "value": "Custom Value 1"},
            {"custom_field_definition_id": "2", "value": "Custom Value 2"}
        ]
    }


@pytest.mark.asyncio
async def test_list_people(client, mock_base_client):
    """Test listing people with pagination."""
    mock_response = {
        "items": [
            {
                "id": "1",
                "name": "Test Person",
                "emails": [{"email": "test@example.com", "category": "work"}],
                "phone_numbers": [{"number": "123-456-7890", "category": "work"}],
                "socials": [],
                "websites": []
            }
        ],
        "total": 1,
        "page": 1,
        "page_size": 10
    }
    mock_base_client.get.return_value = mock_response
    
    result = await client.list(page_size=10, page_number=1)
    assert len(result) == 1
    assert isinstance(result[0], Person)
    assert result[0].id == "1"
    assert result[0].name == "Test Person"
    assert result[0].emails[0].email == "test@example.com"
    mock_base_client.get.assert_called_once_with("/people", params={"page_size": 10, "page": 1})


@pytest.mark.asyncio
async def test_get_person(client, mock_base_client, mock_person):
    """Test getting a person by ID."""
    mock_base_client.get.return_value = mock_person
    
    person = await client.get("12345")
    assert isinstance(person, Person)
    assert person.id == "12345"
    assert person.name == "John Doe"
    assert len(person.emails) == 2
    assert person.emails[0].email == "john@example.com"
    mock_base_client.get.assert_called_once_with("/people/12345")


@pytest.mark.asyncio
async def test_create_person(client, mock_base_client, mock_person):
    """Test creating a new person."""
    mock_base_client.post.return_value = mock_person
    
    person_data = PersonCreate(
        name="John Doe",
        emails=[EmailPhone(email="john@example.com", category="work")]
    )
    
    person = await client.create(person_data)
    
    assert isinstance(person, Person)
    assert person.name == "John Doe"
    mock_base_client.post.assert_called_once_with("/people", person_data.dict(exclude_unset=True))


@pytest.mark.asyncio
async def test_update_person(client, mock_base_client, mock_person):
    """Test updating an existing person."""
    mock_base_client.put.return_value = mock_person
    
    person_data = PersonUpdate(name="John Updated")
    
    person = await client.update("12345", person_data)
    
    assert isinstance(person, Person)
    assert person.id == "12345"
    mock_base_client.put.assert_called_once_with("/people/12345", person_data.dict(exclude_unset=True))


@pytest.mark.asyncio
async def test_delete_person(client, mock_base_client):
    """Test deleting a person."""
    mock_base_client.delete.return_value = None
    
    await client.delete("12345")
    mock_base_client.delete.assert_called_once_with("/people/12345")


@pytest.mark.asyncio
async def test_search_people(client, mock_base_client, mock_person):
    """Test searching for people."""
    mock_response = {
        "items": [mock_person],
        "total": 1,
        "page": 1,
        "page_size": 10
    }
    mock_base_client.post.return_value = mock_response
    
    search_params = {"query": "John"}
    
    results = await client.search(search_params)
    
    assert len(results) == 1
    assert isinstance(results[0], Person)
    assert results[0].name == "John Doe"
    mock_base_client.post.assert_called_once_with("/people/search", search_params)


@pytest.mark.asyncio
async def test_update_custom_fields(client, mock_base_client, mock_person):
    """Test updating custom fields."""
    custom_fields = [CustomField(custom_field_definition_id="1", value="test")]
    mock_person["custom_fields"] = [cf.dict() for cf in custom_fields]
    mock_base_client.put.return_value = mock_person
    
    result = await client.update_custom_fields("1", custom_fields)
    assert isinstance(result, Person)
    assert result.id == "12345"
    assert len(result.custom_fields) == 1
    assert result.custom_fields[0].custom_field_definition_id == "1"
    assert result.custom_fields[0].value == "test"
    mock_base_client.put.assert_called_once_with("/people/1/custom_fields", {"custom_fields": [cf.dict() for cf in custom_fields]})


@pytest.mark.asyncio
async def test_convert_lead(client, mock_base_client, mock_person):
    """Test converting a lead to a person."""
    mock_base_client.post.return_value = mock_person
    
    details = {"status": "converted"}
    
    result = await client.convert_lead("1", details)
    assert isinstance(result, Person)
    assert result.id == "12345"
    assert result.name == "John Doe"
    mock_base_client.post.assert_called_once_with("/leads/1/convert", details)


@pytest.mark.asyncio
async def test_get_related(client, mock_base_client):
    """Test getting related entities."""
    expected = {"items": [{"id": "1", "type": "opportunity"}]}
    mock_base_client.get.return_value = expected
    
    result = await client.get_related("1")
    assert len(result) == 1
    assert result[0]["id"] == "1"
    assert result[0]["type"] == "opportunity"
    mock_base_client.get.assert_called_once_with("/people/1/related")