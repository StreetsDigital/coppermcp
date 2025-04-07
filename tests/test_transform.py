"""Tests for data transformation between Copper and MCP formats."""
import pytest
from datetime import datetime, UTC
from typing import Dict, Any, List, Literal, Optional
from pydantic import BaseModel, Field, ValidationError

from app.mapping.transform import BaseTransformer, TransformationError
from app.models.copper import Person, Company, Opportunity, Activity
from app.models.mcp import (
    MCPPerson, MCPCompany, MCPOpportunity, MCPActivity,
    MCPBase, MCPAttributes
)

class ComplexTestModel(BaseModel):
    """Complex test model with nested data."""
    id: int
    required_str: str
    integer_value: int = Field(gt=0)  # Must be greater than 0
    nested_dict: Dict[str, Any]
    date_created: Optional[datetime] = None
    date_modified: Optional[datetime] = None

class ComplexMCPAttributes(MCPAttributes):
    """Complex test MCP attributes."""
    value: int
    nested_data: Dict[str, Any]

class ComplexMCPModel(MCPBase):
    """Complex MCP model for testing."""
    type: Literal["complex"]
    attributes: ComplexMCPAttributes

class ComplexTransformer(BaseTransformer[ComplexTestModel, ComplexMCPModel]):
    """Test transformer for complex data structures."""
    
    def __init__(self):
        """Initialize the transformer."""
        super().__init__(ComplexTestModel, ComplexMCPModel)
    
    def _to_mcp_format(self, data: ComplexTestModel) -> Dict[str, Any]:
        """Transform complex test data to MCP format."""
        return {
            "type": "complex",
            "attributes": {
                "name": data.required_str,
                "value": data.integer_value,
                "nested_data": data.nested_dict
            }
        }
    
    def transform_list_to_mcp(self, data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform a list of data to MCP format."""
        return [self.to_mcp(item) for item in data_list]

def test_transform_minimal_data():
    """Test transformation with minimal required data."""
    transformer = ComplexTransformer()
    input_data = {
        "id": 1,
        "required_str": "test",
        "integer_value": 1,
        "nested_dict": {},
        "date_created": datetime.now(UTC),
        "date_modified": datetime.now(UTC)
    }
    
    result = transformer.to_mcp(input_data)
    
    assert result["type"] == "complex"
    assert result["source"] == "copper"
    assert result["source_id"] == "1"
    assert result["attributes"]["name"] == "test"
    assert result["attributes"]["value"] == 1
    assert result["attributes"]["nested_data"] == {}
    assert "created_at" in result["attributes"]
    assert "updated_at" in result["attributes"]

def test_transform_full_data():
    """Test transformation with all fields populated."""
    transformer = ComplexTransformer()
    now = datetime.now(UTC)
    input_data = {
        "id": 2,
        "required_str": "test",
        "integer_value": 42,
        "nested_dict": {"key": "value"},
        "date_created": now,
        "date_modified": now
    }
    
    result = transformer.to_mcp(input_data)
    
    assert result["type"] == "complex"
    assert result["source"] == "copper"
    assert result["source_id"] == "2"
    assert result["attributes"]["name"] == "test"
    assert result["attributes"]["value"] == 42
    assert result["attributes"]["nested_data"] == {"key": "value"}
    assert result["attributes"]["created_at"] == now.strftime("%Y-%m-%dT%H:%M:%SZ")
    assert result["attributes"]["updated_at"] == now.strftime("%Y-%m-%dT%H:%M:%SZ")

def test_transform_empty_string():
    """Test handling of empty strings."""
    transformer = ComplexTransformer()
    now = datetime.now(UTC)
    input_data = {
        "id": 3,
        "required_str": "",  # Empty string
        "integer_value": 1,
        "nested_dict": {},
        "date_created": now,
        "date_modified": now
    }
    
    result = transformer.to_mcp(input_data)
    assert result["attributes"]["name"] == ""

def test_transform_whitespace_string():
    """Test handling of whitespace strings."""
    transformer = ComplexTransformer()
    now = datetime.now(UTC)
    input_data = {
        "id": 4,
        "required_str": "   spaced   ",
        "integer_value": 1,
        "nested_dict": {},
        "date_created": now,
        "date_modified": now
    }
    
    result = transformer.to_mcp(input_data)
    assert result["attributes"]["name"] == "   spaced   "

def test_transform_zero_value():
    """Test validation of integer greater than zero."""
    transformer = ComplexTransformer()
    now = datetime.now(UTC)
    input_data = {
        "id": 5,
        "required_str": "test",
        "integer_value": 0,  # Should fail validation
        "nested_dict": {},
        "date_created": now,
        "date_modified": now
    }
    
    with pytest.raises(ValidationError) as exc_info:
        transformer.to_mcp(input_data)
    assert "greater than 0" in str(exc_info.value)

def test_transform_empty_list():
    """Test transformation of empty list."""
    transformer = ComplexTransformer()
    input_data_list: List[Dict[str, Any]] = []
    
    result = transformer.transform_list_to_mcp(input_data_list)
    assert isinstance(result, list)
    assert len(result) == 0

def test_transform_list_with_invalid_item():
    """Test list transformation with one invalid item."""
    transformer = ComplexTransformer()
    input_data_list = [
        {"id": 6, "required_str": "valid", "integer_value": 1, "nested_dict": {}},
        {"required_str": "invalid"}  # Missing required fields
    ]
    
    with pytest.raises(ValidationError):
        transformer.transform_list_to_mcp(input_data_list)

def test_transform_nested_empty_dict():
    """Test handling of empty nested dictionary."""
    transformer = ComplexTransformer()
    now = datetime.now(UTC)
    input_data = {
        "id": 7,
        "required_str": "test",
        "integer_value": 1,
        "nested_dict": {},
        "date_created": now,
        "date_modified": now
    }
    
    result = transformer.to_mcp(input_data)
    assert result["attributes"]["nested_data"] == {}

def test_transform_complex_nested_data():
    """Test handling of complex nested data structures."""
    transformer = ComplexTransformer()
    now = datetime.now(UTC)
    input_data = {
        "id": 8,
        "required_str": "test",
        "integer_value": 1,
        "nested_dict": {
            "level1": {
                "level2": [1, 2, 3],
                "data": {"a": 1, "b": 2}
            }
        },
        "date_created": now,
        "date_modified": now
    }
    
    result = transformer.to_mcp(input_data)
    assert result["type"] == "complex"
    assert result["source"] == "copper"
    assert result["source_id"] == "8"
    assert result["attributes"]["name"] == "test"
    assert result["attributes"]["value"] == 1
    assert result["attributes"]["nested_data"]["level1"]["level2"] == [1, 2, 3]
    assert result["attributes"]["nested_data"]["level1"]["data"] == {"a": 1, "b": 2}

def test_base_transformer_validation():
    """Test that base transformer properly validates input and output."""
    class TestModel(BaseModel):
        id: int
        name: str
        date_created: datetime
        date_modified: datetime
    
    class TestMCPAttributes(MCPAttributes):
        value: Optional[str] = None
    
    class TestMCPModel(MCPBase):
        type: Literal["test"]
        attributes: TestMCPAttributes
    
    class TestTransformer(BaseTransformer[TestModel, TestMCPModel]):
        def _to_mcp_format(self, data: TestModel) -> Dict[str, Any]:
            return {
                "type": "test",
                "attributes": {
                    "name": data.name,
                    "value": None
                }
            }
    
    transformer = TestTransformer(TestModel, TestMCPModel)
    
    # Test with valid data
    now = datetime.now(UTC)
    result = transformer.to_mcp({
        "id": 123,
        "name": "Test",
        "date_created": now,
        "date_modified": now
    })
    
    assert result["type"] == "test"
    assert result["source"] == "copper"
    assert result["source_id"] == "123"
    assert result["attributes"]["created_at"] == now.strftime("%Y-%m-%dT%H:%M:%SZ")
    assert result["attributes"]["updated_at"] == now.strftime("%Y-%m-%dT%H:%M:%SZ")

def test_relationship_creation():
    """Test creation of MCP relationships."""
    class TestModel(BaseModel):
        id: int
        date_created: datetime
        date_modified: datetime
    
    class TestMCPModel(MCPBase):
        type: Literal["test"]
        attributes: MCPAttributes
    
    class TestTransformer(BaseTransformer[TestModel, TestMCPModel]):
        def _to_mcp_format(self, data: TestModel) -> Dict[str, Any]:
            return {
                "type": "test",
                "attributes": {}
            }
    
    transformer = TestTransformer(TestModel, TestMCPModel)
    
    # Test with valid relationship
    rel = transformer._create_relationship("user", 123, "Test User")
    assert rel["data"]["type"] == "user"
    assert rel["data"]["id"] == "123"
    assert rel["data"]["name"] == "Test User"
    
    # Test with missing ID
    rel = transformer._create_relationship("user", None)
    assert rel["data"] is None
    
    # Test without name
    rel = transformer._create_relationship("user", 123)
    assert rel["data"]["type"] == "user"
    assert rel["data"]["id"] == "123"
    assert "name" not in rel["data"]

def test_datetime_formatting():
    """Test datetime formatting to ISO8601."""
    class TestModel(BaseModel):
        id: int
        date_created: datetime
        date_modified: datetime
    
    class TestMCPModel(MCPBase):
        type: Literal["test"]
        attributes: MCPAttributes
    
    class TestTransformer(BaseTransformer[TestModel, TestMCPModel]):
        def _to_mcp_format(self, data: TestModel) -> Dict[str, Any]:
            return {
                "type": "test",
                "attributes": {}
            }
    
    transformer = TestTransformer(TestModel, TestMCPModel)
    
    dt = datetime(2024, 3, 19, 12, 34, 56, tzinfo=UTC)
    formatted = transformer._format_datetime(dt)
    assert formatted == "2024-03-19T12:34:56Z"
    
    assert transformer._format_datetime(None) is None

def test_primary_contact_extraction():
    """Test extraction of primary contact methods."""
    class TestModel(BaseModel):
        id: int
    
    class TestMCPModel(MCPBase):
        type: str = "test"
        attributes: MCPAttributes
    
    transformer = BaseTransformer(TestModel, TestMCPModel)
    
    contacts = [
        {"category": "work", "type": "phone", "value": "123-work"},
        {"category": "home", "type": "phone", "value": "123-home"}
    ]
    
    # Test work contact priority
    assert transformer._get_primary_contact(contacts) == "123-work"
    
    # Test fallback to first contact
    contacts = [
        {"category": "home", "type": "phone", "value": "123-home"},
        {"category": "other", "type": "phone", "value": "123-other"}
    ]
    assert transformer._get_primary_contact(contacts) == "123-home"
    
    # Test empty contacts
    assert transformer._get_primary_contact([]) is None

def test_mcp_format_compliance():
    """Test that transformed data complies with MCP format."""
    class TestModel(BaseModel):
        id: int
        name: str
        date_created: datetime
        date_modified: datetime
    
    class TestMCPAttributes(MCPAttributes):
        value: Optional[str] = None
    
    class TestMCPModel(MCPBase):
        type: Literal["test"]
        attributes: TestMCPAttributes
    
    class TestTransformer(BaseTransformer[TestModel, TestMCPModel]):
        def _to_mcp_format(self, data: TestModel) -> Dict[str, Any]:
            return {
                "type": "test",
                "attributes": {
                    "name": data.name,
                    "value": None
                }
            }
    
    transformer = TestTransformer(TestModel, TestMCPModel)
    now = datetime.now(UTC)
    
    result = transformer.to_mcp({
        "id": 123,
        "name": "Test",
        "date_created": now,
        "date_modified": now
    })
    
    # Verify MCP format compliance
    assert isinstance(result, dict)
    assert "type" in result
    assert "attributes" in result
    assert "relationships" in result
    assert "meta" in result
    assert isinstance(result["attributes"], dict)
    assert isinstance(result["relationships"], dict)
    assert isinstance(result["meta"], dict)
    
    # Verify required fields
    assert result["type"] == "test"
    assert result["source"] == "copper"
    assert result["source_id"] == "123"
    
    # Verify timestamps
    assert result["attributes"]["created_at"] == now.strftime("%Y-%m-%dT%H:%M:%SZ")
    assert result["attributes"]["updated_at"] == now.strftime("%Y-%m-%dT%H:%M:%SZ") 