"""Tests for the OpportunityTransformer class."""
from datetime import datetime
from app.mapping.opportunity import OpportunityTransformer
from app.models.copper import Opportunity

def test_transform_minimal_opportunity():
    """Test transformation of opportunity with minimal data."""
    transformer = OpportunityTransformer()
    data = {
        "name": "Test Opportunity",
        "status": "open",
        "pipeline_id": 123,
        "pipeline_stage_id": 456,
        "monetary_value": 1000,
        "win_probability": 50,
        "close_date": 1234567890
    }
    
    result = transformer.transform(data)
    
    assert result["type"] == "opportunity"
    assert result["attributes"]["name"] == "Test Opportunity"
    assert result["attributes"]["status"] == "open"
    assert result["attributes"]["pipeline_id"] == "123"
    assert result["attributes"]["pipeline_stage_id"] == "456"
    assert result["attributes"]["monetary_value"] == 1000
    assert result["attributes"]["win_probability"] == 50

def test_transform_full_opportunity():
    """Test transformation of opportunity with all fields populated."""
    transformer = OpportunityTransformer()
    data = {
        "id": 789,
        "name": "Full Opportunity",
        "status": "won",
        "pipeline_id": 123,
        "pipeline_stage_id": 456,
        "monetary_value": 5000,
        "win_probability": 75,
        "close_date": 1234567890,
        "date_created": 1234567800,
        "date_modified": 1234567850,
        "primary_contact_id": 101,
        "company_id": 102,
        "assignee_id": 103,
        "custom_fields": [
            {"custom_field_definition_id": 201, "value": "Custom value"}
        ]
    }
    
    result = transformer.transform(data)
    
    assert result["type"] == "opportunity"
    assert result["attributes"]["name"] == "Full Opportunity"
    assert result["attributes"]["status"] == "won"
    assert result["attributes"]["pipeline_id"] == "123"
    assert result["attributes"]["pipeline_stage_id"] == "456"
    assert result["attributes"]["monetary_value"] == 5000
    assert result["attributes"]["win_probability"] == 75
    assert result["relationships"]["primary_contact"]["data"]["id"] == "101"
    assert result["relationships"]["company"]["data"]["id"] == "102"
    assert result["relationships"]["assignee"]["data"]["id"] == "103"
    assert result["meta"]["custom_fields"]["201"] == "Custom value"

def test_transform_status_transitions():
    """Test transformation with different opportunity statuses."""
    transformer = OpportunityTransformer()
    statuses = ["open", "won", "lost", "abandoned"]
    
    for status in statuses:
        data = {
            "name": "Status Test",
            "status": status,
            "pipeline_id": 123,
            "pipeline_stage_id": 456,
            "monetary_value": 1000,
            "win_probability": 50,
            "close_date": 1234567890
        }
        result = transformer.transform(data)
        assert result["attributes"]["status"] == status

def test_transform_empty_lists():
    """Test transformation with empty lists and optional fields."""
    transformer = OpportunityTransformer()
    data = {
        "name": "Empty Lists",
        "status": "open",
        "pipeline_id": 123,
        "pipeline_stage_id": 456,
        "monetary_value": 1000,
        "win_probability": 50,
        "close_date": 1234567890,
        "custom_fields": []
    }
    
    result = transformer.transform(data)
    
    assert result["meta"]["custom_fields"] == {}

def test_transform_validation():
    """Test validation of opportunity data."""
    transformer = OpportunityTransformer()
    invalid_data = {
        "name": "Invalid",
        "status": "invalid_status",  # Invalid status
        "pipeline_id": 123,
        "pipeline_stage_id": 456,
        "monetary_value": "not_a_number",  # Invalid monetary value
        "win_probability": 150,  # Invalid probability
        "close_date": "not_a_timestamp"  # Invalid date
    }
    
    try:
        transformer.transform(invalid_data)
        assert False, "Should have raised validation error"
    except Exception as e:
        assert "validation" in str(e).lower() 