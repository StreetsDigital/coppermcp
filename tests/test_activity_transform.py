"""Tests for the Activity transformer."""
import pytest
from datetime import datetime

from app.mapping.activity import ActivityTransformer
from app.copper.models.activities import Activity, ActivityCreate
from app.copper.models.base import Parent

def test_transform_minimal_activity():
    """Test transforming an activity with minimal data."""
    data = {
        "type": {"category": "user", "id": 123},
        "details": "Test note",
        "activity_date": 1234567890,
        "parent": {"type": "person", "id": 456}
    }
    
    transformer = ActivityTransformer(ActivityCreate)
    result = transformer.transform_to_mcp(data)
    
    assert result["type"] == "activity"
    assert result["id"] is None
    assert result["attributes"]["activity_type"] == {"category": "user", "id": "123"}
    assert result["attributes"]["details"] == "Test note"
    assert result["attributes"]["activity_date"] == "2009-02-13T23:31:30Z"
    assert result["relationships"]["parent"]["data"] == {"type": "person", "id": "456"}
    assert result["relationships"]["user"]["data"] is None
    assert result["relationships"]["assignee"]["data"] is None
    assert result["meta"]["custom_fields"] == {}

def test_transform_full_activity():
    """Test transforming an activity with all fields populated."""
    data = {
        "id": 789,
        "type": {"category": "user", "id": 123},
        "details": "Important meeting",
        "activity_date": 1234567890,
        "date_created": 1234567800,
        "date_modified": 1234567850,
        "parent": {"type": "company", "id": 456},
        "user_id": 101,
        "assignee_id": 102,
        "custom_fields": [
            {"custom_field_definition_id": 201, "value": "Custom value"}
        ]
    }
    
    transformer = ActivityTransformer(Activity)
    result = transformer.transform_to_mcp(data)
    
    assert result["type"] == "activity"
    assert result["id"] == "789"
    assert result["attributes"]["activity_type"] == {"category": "user", "id": "123"}
    assert result["attributes"]["details"] == "Important meeting"
    assert result["attributes"]["activity_date"] == "2009-02-13T23:31:30Z"
    assert result["attributes"]["created_at"] == "2009-02-13T23:30:00Z"
    assert result["attributes"]["updated_at"] == "2009-02-13T23:30:50Z"
    assert result["relationships"]["parent"]["data"] == {"type": "company", "id": "456"}
    assert result["relationships"]["user"]["data"] == {"type": "user", "id": "101"}
    assert result["relationships"]["assignee"]["data"] == {"type": "user", "id": "102"}
    assert result["meta"]["custom_fields"] == {"201": "Custom value"}

def test_transform_validation():
    """Test validation of activity data."""
    data = {
        "type": {"category": "invalid", "id": 123},
        "details": "Test note",
        "activity_date": 1234567890,
        "parent": {"type": "person", "id": 456}
    }
    
    transformer = ActivityTransformer(ActivityCreate)
    with pytest.raises(ValueError):
        transformer.transform_to_mcp(data)

def test_transform_empty_custom_fields():
    """Test transforming an activity with empty custom fields."""
    data = {
        "type": {"category": "user", "id": 123},
        "details": "Test note",
        "activity_date": 1234567890,
        "parent": {"type": "person", "id": 456},
        "custom_fields": []
    }
    
    transformer = ActivityTransformer(ActivityCreate)
    result = transformer.transform_to_mcp(data)
    
    assert result["meta"]["custom_fields"] == {} 