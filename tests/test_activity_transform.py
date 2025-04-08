"""Tests for the ActivityTransformer class."""
from datetime import datetime, timezone
import pytest
from pydantic import HttpUrl

from app.models.copper import Activity, ActivityType, ParentEntity
from app.models.mcp import MCPActivity
from app.mapping.activity import ActivityTransformer

@pytest.fixture
def transformer():
    """Create an activity transformer for testing."""
    return ActivityTransformer(copper_model=Activity, mcp_model=MCPActivity)

def test_transform_minimal_activity(transformer):
    """Test transforming an activity with minimal data."""
    data = {
        "id": 123,
        "type": {"category": "user", "id": 123},
        "details": "Test note",
        "activity_date": int(datetime.now(timezone.utc).timestamp()),
        "parent": {"type": "person", "id": 456}
    }
    
    result = transformer.to_mcp(data)
    assert result["type"] == "activity"
    assert result["source"] == "copper"
    assert result["source_id"] == "123"
    assert result["attributes"]["details"] == "Test note"

def test_transform_full_activity(transformer):
    """Test transforming an activity with all fields populated."""
    now = int(datetime.now(timezone.utc).timestamp())
    data = {
        "id": 789,
        "type": {"category": "user", "id": 123},
        "details": "Important meeting",
        "activity_date": now,
        "date_created": now,
        "date_modified": now,
        "parent": {"type": "company", "id": 456},
        "user_id": 101,
        "assignee_id": 102,
        "custom_fields": [
            {"custom_field_definition_id": 201, "value": "Custom value"}
        ]
    }
    
    result = transformer.to_mcp(data)
    assert result["type"] == "activity"
    assert result["source"] == "copper"
    assert result["source_id"] == "789"
    assert result["attributes"]["details"] == "Important meeting"
    assert result["attributes"]["activity_type"] == "user"
    assert result["relationships"]["parent"]["type"] == "company"
    assert result["relationships"]["parent"]["id"] == "456"
    assert result["meta"]["custom_fields"][0]["value"] == "Custom value"

def test_transform_validation(transformer):
    """Test validation of activity data."""
    data = {
        "id": 123,
        "type": {"category": "invalid", "id": 123},
        "details": "Test note",
        "activity_date": int(datetime.now(timezone.utc).timestamp()),
        "parent": {"type": "person", "id": 456}
    }
    
    with pytest.raises(ValueError):
        transformer.to_mcp(data)

def test_transform_empty_custom_fields(transformer):
    """Test transforming an activity with empty custom fields."""
    data = {
        "id": 123,
        "type": {"category": "user", "id": 123},
        "details": "Test note",
        "activity_date": int(datetime.now(timezone.utc).timestamp()),
        "parent": {"type": "person", "id": 456},
        "custom_fields": []
    }
    
    result = transformer.to_mcp(data)
    assert result["meta"]["custom_fields"] == [] 