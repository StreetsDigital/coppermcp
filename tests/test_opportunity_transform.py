"""Tests for the OpportunityTransformer class."""
from datetime import datetime, timezone
import pytest
from pydantic import HttpUrl

from app.mapping.opportunity import OpportunityTransformer
from app.models.copper import Opportunity
from app.models.mcp import MCPOpportunity

@pytest.fixture
def transformer():
    """Create an opportunity transformer for testing."""
    return OpportunityTransformer(copper_model=Opportunity, mcp_model=MCPOpportunity)

def test_transform_minimal_opportunity(transformer):
    """Test transforming an opportunity with minimal data."""
    data = {
        "id": 123,
        "name": "Test Deal",
        "status": "Open",
        "pipeline_id": 1,
        "pipeline_stage_id": 2,
        "details": None,
        "monetary_value": None,
        "win_probability": None,
        "close_date": None,
        "custom_fields": []
    }
    
    result = transformer.to_mcp(data)
    assert result["type"] == "opportunity"
    assert result["source"] == "copper"
    assert result["source_id"] == "123"
    assert result["attributes"]["name"] == "Test Deal"
    assert result["attributes"]["status"] == "Open"
    assert result["attributes"]["pipeline_id"] == "1"
    assert result["attributes"]["pipeline_stage_id"] == "2"

def test_transform_full_opportunity(transformer):
    """Test transforming an opportunity with all fields populated."""
    now = int(datetime.now(timezone.utc).timestamp())
    data = {
        "id": 789,
        "name": "Big Deal",
        "status": "Won",
        "pipeline_id": 3,
        "pipeline_stage_id": 4,
        "details": "Opportunity details",
        "monetary_value": 100000,
        "win_probability": 75,
        "close_date": now,
        "date_created": now,
        "date_modified": now,
        "assignee_id": 101,
        "company_id": 201,
        "primary_contact_id": 301,
        "custom_fields": [
            {"custom_field_definition_id": 201, "value": "Custom value"}
        ]
    }
    
    result = transformer.to_mcp(data)
    assert result["type"] == "opportunity"
    assert result["source"] == "copper"
    assert result["source_id"] == "789"
    assert result["attributes"]["name"] == "Big Deal"
    assert result["attributes"]["status"] == "Won"
    assert result["attributes"]["pipeline_id"] == "3"
    assert result["attributes"]["pipeline_stage_id"] == "4"
    assert result["attributes"]["details"] == "Opportunity details"
    assert result["attributes"]["monetary_value"] == 100000
    assert result["attributes"]["win_probability"] == 75
    assert result["attributes"]["close_date"] == now
    assert result["relationships"]["company"]["data"]["id"] == "201"
    assert result["relationships"]["primary_contact"]["data"]["id"] == "301"
    assert result["meta"]["custom_fields"][0]["value"] == "Custom value"

def test_transform_validation(transformer):
    """Test validation of opportunity data."""
    data = {
        "id": 123,
        "name": "",  # Invalid empty name
        "status": "Invalid",  # Invalid status
        "pipeline_id": 1,
        "pipeline_stage_id": 2,
        "details": None,
        "monetary_value": -1000,  # Invalid negative value
        "win_probability": 101,  # Invalid probability > 100
        "close_date": None,
        "custom_fields": []
    }
    
    with pytest.raises(ValueError):
        transformer.to_mcp(data)

def test_transform_empty_custom_fields(transformer):
    """Test transforming an opportunity with empty custom fields."""
    data = {
        "id": 123,
        "name": "Test Deal",
        "status": "Open",
        "pipeline_id": 1,
        "pipeline_stage_id": 2,
        "details": None,
        "monetary_value": None,
        "win_probability": None,
        "close_date": None,
        "custom_fields": []
    }
    
    result = transformer.to_mcp(data)
    assert result["meta"]["custom_fields"] == []

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