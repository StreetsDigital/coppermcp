"""Tests for the ActivityTransformer class."""
from app.mapping.activity import ActivityTransformer
from app.models.copper import Activity, ActivityCreate

def test_transform_minimal_activity():
    """Test transforming an activity with minimal data."""
    data = {
        "type": {"category": "user", "id": 123},
        "details": "Test note",
        "activity_date": 1234567890,
        "parent": {"type": "person", "id": 456}
    }

    transformer = ActivityTransformer()
    result = transformer.transform(data)

    assert result["type"] == "activity"
    assert result["attributes"]["details"] == "Test note"
    assert result["attributes"]["activity_type"]["category"] == "user"
    assert result["attributes"]["activity_type"]["id"] == "123"
    assert result["relationships"]["parent"]["data"]["type"] == "person"
    assert result["relationships"]["parent"]["data"]["id"] == "456"

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

    transformer = ActivityTransformer()
    result = transformer.transform(data)

    assert result["type"] == "activity"
    assert result["attributes"]["details"] == "Important meeting"
    assert result["attributes"]["activity_type"]["category"] == "user"
    assert result["attributes"]["activity_type"]["id"] == "123"
    assert result["relationships"]["parent"]["data"]["type"] == "company"
    assert result["relationships"]["parent"]["data"]["id"] == "456"
    assert result["relationships"]["user"]["data"]["type"] == "user"
    assert result["relationships"]["user"]["data"]["id"] == "101"
    assert result["relationships"]["assignee"]["data"]["type"] == "user"
    assert result["relationships"]["assignee"]["data"]["id"] == "102"
    assert result["meta"]["custom_fields"]["201"] == "Custom value"

def test_transform_validation():
    """Test validation of activity data."""
    data = {
        "type": {"category": "invalid", "id": 123},
        "details": "Test note",
        "activity_date": 1234567890,
        "parent": {"type": "person", "id": 456}
    }

    transformer = ActivityTransformer()
    try:
        transformer.transform(data)
        assert False, "Should have raised validation error"
    except Exception as e:
        assert "validation" in str(e).lower()

def test_transform_empty_custom_fields():
    """Test transforming an activity with empty custom fields."""
    data = {
        "type": {"category": "user", "id": 123},
        "details": "Test note",
        "activity_date": 1234567890,
        "parent": {"type": "person", "id": 456},
        "custom_fields": []
    }

    transformer = ActivityTransformer()
    result = transformer.transform(data)

    assert result["meta"]["custom_fields"] == {} 