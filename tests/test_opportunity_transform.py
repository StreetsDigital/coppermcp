"""Tests for the Opportunity transformer."""
from datetime import datetime
from app.mapping.opportunity import OpportunityTransformer
from app.models.copper import Opportunity

def test_transform_minimal_opportunity():
    """Test transformation of opportunity with minimal data."""
    transformer = OpportunityTransformer(Opportunity)
    input_data = {
        "name": "Basic Deal",
        "status": "Open"
    }

    result = transformer.transform_to_mcp(input_data)

    # Check basic attributes
    assert result["type"] == "opportunity"
    assert result["id"] is None  # No ID provided
    assert result["attributes"]["name"] == "Basic Deal"
    assert result["attributes"]["status"] == "Open"
    assert result["attributes"]["monetary_value"] is None
    assert result["attributes"]["win_probability"] is None
    assert result["meta"]["interaction_count"] == 0
    assert result["meta"]["custom_fields"] == {}

def test_transform_full_opportunity():
    """Test transformation of opportunity with all fields populated."""
    transformer = OpportunityTransformer(Opportunity)
    input_data = {
        "id": 123,
        "name": "Enterprise License Deal",
        "status": "Open",
        "priority": "High",
        "monetary_value": 100000.00,
        "win_probability": 75.0,
        "details": "Annual enterprise license renewal",
        "close_date": "2024-12-31T23:59:59Z",
        "assignee_id": 456,
        "company_id": 789,
        "company_name": "ACME Corp",
        "pipeline_id": 1,
        "pipeline_stage_id": 2,
        "tags": ["Enterprise", "Renewal"],
        "custom_fields": [
            {"custom_field_definition_id": 1, "value": "Q4 2024"}
        ],
        "date_created": "2024-01-01T00:00:00Z",
        "date_modified": "2024-01-02T00:00:00Z",
        "interaction_count": 5
    }

    result = transformer.transform_to_mcp(input_data)

    # Check basic attributes
    assert result["type"] == "opportunity"
    assert result["id"] == "123"
    assert result["attributes"]["name"] == "Enterprise License Deal"
    assert result["attributes"]["status"] == "Open"
    assert result["attributes"]["priority"] == "High"
    assert result["attributes"]["monetary_value"] == 100000.00
    assert result["attributes"]["win_probability"] == 75.0
    assert result["attributes"]["details"] == "Annual enterprise license renewal"
    assert result["attributes"]["close_date"] == "2024-12-31T23:59:59Z"
    assert result["attributes"]["tags"] == ["Enterprise", "Renewal"]
    assert result["attributes"]["created_at"] == "2024-01-01T00:00:00Z"
    assert result["attributes"]["updated_at"] == "2024-01-02T00:00:00Z"

    # Check relationships
    assert result["relationships"]["assignee"]["data"]["type"] == "user"
    assert result["relationships"]["assignee"]["data"]["id"] == "456"
    
    assert result["relationships"]["company"]["data"]["type"] == "company"
    assert result["relationships"]["company"]["data"]["id"] == "789"
    assert result["relationships"]["company"]["data"]["name"] == "ACME Corp"
    
    assert result["relationships"]["pipeline"]["data"]["type"] == "pipeline"
    assert result["relationships"]["pipeline"]["data"]["id"] == "1"
    
    assert result["relationships"]["pipeline_stage"]["data"]["type"] == "pipeline_stage"
    assert result["relationships"]["pipeline_stage"]["data"]["id"] == "2"

    # Check metadata
    assert result["meta"]["interaction_count"] == 5
    assert result["meta"]["custom_fields"]["1"] == "Q4 2024"

def test_transform_status_transitions():
    """Test transformation with different opportunity statuses."""
    transformer = OpportunityTransformer(Opportunity)
    statuses = ["Open", "Won", "Lost", "Abandoned"]

    for status in statuses:
        input_data = {
            "name": f"{status} Deal",
            "status": status
        }
        result = transformer.transform_to_mcp(input_data)
        assert result["attributes"]["status"] == status

def test_transform_empty_lists():
    """Test transformation with empty lists and optional fields."""
    transformer = OpportunityTransformer(Opportunity)
    input_data = {
        "name": "Empty Deal",
        "status": "Open",
        "tags": [],
        "custom_fields": []
    }

    result = transformer.transform_to_mcp(input_data)

    assert result["attributes"]["tags"] == []
    assert result["meta"]["custom_fields"] == {}
    assert result["relationships"]["assignee"]["data"] is None
    assert result["relationships"]["company"]["data"] is None
    assert result["relationships"]["pipeline"]["data"] is None
    assert result["relationships"]["pipeline_stage"]["data"] is None

def test_transform_validation():
    """Test validation of opportunity data."""
    transformer = OpportunityTransformer(Opportunity)
    
    # Test invalid status
    try:
        input_data = {
            "name": "Invalid Deal",
            "status": "Invalid"
        }
        transformer.transform_to_mcp(input_data)
        assert False, "Should raise validation error for invalid status"
    except Exception as e:
        assert "status" in str(e)

    # Test invalid priority
    try:
        input_data = {
            "name": "Invalid Priority Deal",
            "status": "Open",
            "priority": "Invalid"
        }
        transformer.transform_to_mcp(input_data)
        assert False, "Should raise validation error for invalid priority"
    except Exception as e:
        assert "priority" in str(e)

    # Test negative monetary value
    try:
        input_data = {
            "name": "Negative Deal",
            "status": "Open",
            "monetary_value": -1000
        }
        transformer.transform_to_mcp(input_data)
        assert False, "Should raise validation error for negative monetary value"
    except Exception as e:
        assert "monetary_value" in str(e)

    # Test invalid win probability
    try:
        input_data = {
            "name": "Invalid Probability Deal",
            "status": "Open",
            "win_probability": 101
        }
        transformer.transform_to_mcp(input_data)
        assert False, "Should raise validation error for win probability > 100"
    except Exception as e:
        assert "win_probability" in str(e) 