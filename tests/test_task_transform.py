"""Tests for task data transformation between Copper and MCP formats."""
import pytest
from datetime import datetime, timezone
from app.models.copper import Task
from app.models.mcp import MCPTask
from app.mapping.task import TaskTransformer

# Test data
NOW = datetime.now(timezone.utc)
TIMESTAMP = int(NOW.timestamp())

@pytest.fixture
def transformer():
    """Create a task transformer for testing."""
    return TaskTransformer(copper_model=Task, mcp_model=MCPTask)

@pytest.fixture
def copper_task():
    """Create a sample Copper task for testing."""
    return {
        "id": 123,
        "name": "Test Task",
        "assignee_id": 456,
        "due_date": int(datetime.now(timezone.utc).timestamp()),
        "reminder_date": None,
        "completed_date": None,
        "priority": "high",
        "status": "open",
        "details": "Test task details",
        "tags": ["test"],
        "custom_fields": [{"id": 1, "value": "custom value"}],
        "date_created": int(datetime.now(timezone.utc).timestamp()),
        "date_modified": int(datetime.now(timezone.utc).timestamp())
    }

@pytest.fixture
def mcp_task():
    """Create a sample MCP task for testing."""
    return {
        "id": "123",
        "type": "task",
        "source": "copper",
        "source_id": "123",
        "attributes": {
            "name": "Test Task",
            "description": "Test task details",
            "status": "open",
            "priority": "high",
            "due_date": datetime.now(timezone.utc),
            "assignee": "456",
            "completed_date": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        "relationships": {},
        "meta": {
            "custom_fields": [{"id": 1, "value": "custom value"}]
        }
    }

def test_copper_to_mcp(transformer, copper_task):
    """Test conversion from Copper to MCP format."""
    # Convert to Copper model first
    copper_obj = Task(**copper_task)
    
    # Transform to MCP
    result = transformer.to_mcp(copper_obj)
    
    # Verify core fields
    assert result.id == str(copper_task["id"])
    assert result.type == "task"
    assert result.name == copper_task["name"]
    assert result.description == copper_task["details"]
    assert result.status == copper_task["status"]
    assert result.priority == copper_task["priority"]
    
    # Verify dates
    assert result.due_date == NOW
    assert result.reminder_date == NOW
    assert result.completed_date is None
    assert result.created_at == NOW
    assert result.updated_at == NOW
    
    # Verify relationships
    assert result.assignee == str(copper_task["assignee_id"])
    assert result.related_to == {
        "type": copper_task["related_resource"]["type"],
        "id": str(copper_task["related_resource"]["id"])
    }
    
    # Verify arrays and objects
    assert result.tags == copper_task["tags"]
    assert result.metadata == copper_task["custom_fields"]

def test_mcp_to_copper(transformer, mcp_task):
    """Test conversion from MCP to Copper format."""
    # Convert to MCP model first
    mcp_obj = MCPTask(**mcp_task)
    
    # Transform to Copper
    result = transformer.to_copper(mcp_obj)
    
    # Verify core fields
    assert result["name"] == mcp_task["name"]
    assert result["details"] == mcp_task["description"]
    assert result["status"] == mcp_task["status"]
    assert result["priority"] == mcp_task["priority"]
    
    # Verify dates
    assert result["due_date"] == TIMESTAMP
    assert result["reminder_date"] == TIMESTAMP
    assert "completed_date" not in result
    
    # Verify relationships
    assert result["assignee_id"] == int(mcp_task["assignee"])
    assert result["related_resource"] == {
        "type": mcp_task["related_to"]["type"],
        "id": int(mcp_task["related_to"]["id"])
    }
    
    # Verify arrays and objects
    assert result["tags"] == mcp_task["tags"]
    assert result["custom_fields"] == mcp_task["metadata"]

def test_edge_cases(transformer):
    """Test edge cases and optional fields."""
    # Minimal Copper task
    minimal_copper = Task(
        name="Minimal task"
    )
    mcp_result = transformer.to_mcp(minimal_copper)
    assert mcp_result.name == "Minimal task"
    assert mcp_result.status == "open"  # Default value
    assert mcp_result.priority == "none"  # Default value
    
    # Minimal MCP task
    minimal_mcp = MCPTask(
        id="1",
        name="Minimal task"
    )
    copper_result = transformer.to_copper(minimal_mcp)
    assert copper_result["name"] == "Minimal task"
    assert "status" in copper_result
    assert "priority" in copper_result

def test_validation(transformer):
    """Test validation of task data."""
    # Invalid priority
    with pytest.raises(ValueError):
        Task(name="Test", priority="invalid")
    
    # Invalid status
    with pytest.raises(ValueError):
        Task(name="Test", status="invalid")
    
    # Missing required field (name)
    with pytest.raises(ValueError):
        Task()
    
    # Invalid date format
    with pytest.raises(TypeError):
        Task(name="Test", due_date="not a timestamp")

def test_datetime_handling(transformer):
    """Test datetime field handling."""
    # Test with different timezone
    other_tz = datetime.now(timezone.utc).astimezone()
    copper_task = Task(
        name="Test",
        due_date=int(other_tz.timestamp())
    )
    
    mcp_result = transformer.to_mcp(copper_task)
    assert isinstance(mcp_result.due_date, datetime)
    assert mcp_result.due_date.tzinfo == timezone.utc

def test_related_resource_handling(transformer):
    """Test handling of related resources."""
    # Test with different entity types
    entity_types = ["person", "company", "opportunity"]
    
    for entity_type in entity_types:
        copper_task = Task(
            name="Test",
            related_resource={"type": entity_type, "id": 123}
        )
        
        mcp_result = transformer.to_mcp(copper_task)
        assert mcp_result.related_to["type"] == entity_type
        assert mcp_result.related_to["id"] == "123" 