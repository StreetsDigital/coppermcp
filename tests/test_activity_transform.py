"""Tests for the ActivityTransformer class."""
from datetime import datetime, timezone
import pytest
from pydantic import HttpUrl

from app.models.copper import Activity as CopperActivity, ActivityType, ParentEntity, CustomField
from app.models.mcp import Activity as MCPActivity
from app.mapping.activity import ActivityTransformer

@pytest.fixture
def transformer():
    """Create an ActivityTransformer instance for testing."""
    return ActivityTransformer(copper_model=CopperActivity, mcp_model=MCPActivity)

@pytest.fixture
def mock_copper_activity():
    """Create a mock Copper activity for testing."""
    return {
        "id": "12345",
        "activity_type": {
            "id": 1,
            "category": "user",
            "name": "Call"
        },
        "details": "Test activity details",
        "activity_date": int(datetime.now(timezone.utc).timestamp()),
        "user_id": "67890",
        "parent": {
            "id": "54321",
            "type": "person"
        },
        "assignee_id": "98765",
        "custom_fields": [
            {
                "custom_field_definition_id": "cf_1",
                "value": "Test value"
            }
        ]
    }

def test_transform_full_activity(transformer, mock_copper_activity):
    """Test transforming a full activity with all fields."""
    result = transformer.transform(mock_copper_activity)
    assert isinstance(result, dict)
    assert result["id"] == mock_copper_activity["id"]
    assert result["details"] == mock_copper_activity["details"]
    assert result["activity_date"] == mock_copper_activity["activity_date"]
    assert result["user_id"] == mock_copper_activity["user_id"]
    assert result["parent"]["id"] == mock_copper_activity["parent"]["id"]
    assert result["parent"]["type"] == mock_copper_activity["parent"]["type"]
    assert result["assignee_id"] == mock_copper_activity["assignee_id"]
    assert result["custom_fields"][0]["custom_field_definition_id"] == mock_copper_activity["custom_fields"][0]["custom_field_definition_id"]
    assert result["custom_fields"][0]["value"] == mock_copper_activity["custom_fields"][0]["value"]

def test_transform_minimal_activity(transformer, mock_copper_activity):
    """Test transforming a minimal activity."""
    result = transformer.transform(mock_copper_activity)
    assert isinstance(result, dict)
    assert result["id"] == mock_copper_activity["id"]
    assert result["details"] == mock_copper_activity["details"]
    assert result["activity_date"] == mock_copper_activity["activity_date"]
    assert result["user_id"] == mock_copper_activity["user_id"]

def test_transform_validation(transformer):
    """Test validation of required fields."""
    with pytest.raises(ValueError):
        transformer.transform({})

def test_transform_empty_custom_fields(transformer, mock_copper_activity):
    """Test transforming an activity with empty custom fields."""
    mock_copper_activity["custom_fields"] = []
    result = transformer.transform(mock_copper_activity)
    assert isinstance(result, dict)
    assert result["custom_fields"] == []

def test_transform_missing_optional_fields(transformer, mock_copper_activity):
    """Test transforming an activity with missing optional fields."""
    del mock_copper_activity["assignee_id"]
    del mock_copper_activity["custom_fields"]
    result = transformer.transform(mock_copper_activity)
    assert isinstance(result, dict)
    assert "assignee_id" not in result
    assert "custom_fields" not in result

def test_transform_parent_entity(transformer, mock_copper_activity):
    """Test transforming parent entity relationship."""
    result = transformer.transform(mock_copper_activity)
    assert isinstance(result, dict)
    assert result["parent"]["type"] == "person"
    assert result["parent"]["id"] == "54321"

def test_transform_activity_type(transformer, mock_copper_activity):
    """Test transforming activity type."""
    result = transformer.transform(mock_copper_activity)
    assert isinstance(result, dict)
    assert result["activity_type"]["id"] == 1
    assert result["activity_type"]["category"] == "user"
    assert result["activity_type"]["name"] == "Call"

def test_reverse_transform(transformer, mock_copper_activity):
    """Test reverse transformation from MCP to Copper format."""
    mcp_data = transformer.transform(mock_copper_activity)
    result = transformer.reverse_transform(mcp_data)
    
    assert result["activity_type"]["id"] == 1
    assert result["activity_type"]["category"] == "meeting"
    assert result["activity_type"]["name"] == "Client Meeting"
    assert result["details"] == "Meeting with client to discuss project"
    assert result["activity_date"] == 1625097600
    assert result["user_id"] == 101
    assert result["parent"]["type"] == "opportunity"
    assert result["parent"]["id"] == 789
    assert result["assignee_id"] == 202
    assert len(result["custom_fields"]) == 1
    assert result["custom_fields"][0]["custom_field_definition_id"] == 301
    assert result["custom_fields"][0]["value"] == "High Priority"

def test_reverse_transform_minimal(transformer):
    """Test reverse transformation with minimal data."""
    minimal_mcp_data = {
        "type": {
            "id": "1",
            "name": "Call"
        },
        "activity_date": 1625097600,
        "user_id": "101",
        "parent": {
            "type": "person",
            "id": "456"
        }
    }
    
    result = transformer.reverse_transform(minimal_mcp_data)
    
    assert result["activity_type"]["id"] == 1
    assert result["activity_type"]["name"] == "Call"
    assert result["activity_date"] == 1625097600
    assert result["user_id"] == 101
    assert result["parent"]["type"] == "person"
    assert result["parent"]["id"] == 456
    assert "assignee_id" not in result
    assert "custom_fields" not in result

def test_reverse_transform_empty_data(transformer):
    """Test reverse transformation with empty data raises ValueError."""
    with pytest.raises(ValueError, match="Activity data cannot be empty"):
        transformer.reverse_transform({}) 