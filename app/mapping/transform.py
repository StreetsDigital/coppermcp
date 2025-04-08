"""Core transformation module for converting between Copper and MCP formats.

This module provides the base transformation logic and utilities for converting
Copper CRM data into MCP (Model Context Protocol) format.
"""
from typing import Dict, Any, List, Optional, TypeVar, Generic, Type, Union
from datetime import datetime
from pydantic import BaseModel

from app.models.mcp import MCPBase, MCPAttributes, MCPMeta, MCPRelationship

CopperT = TypeVar("CopperT", bound=BaseModel)
MCPT = TypeVar("MCPT", bound=MCPBase)

class BaseTransformer(Generic[CopperT, MCPT]):
    """Base transformer for converting between Copper and MCP data formats."""
    
    def __init__(self, copper_model: type[CopperT], mcp_model: type[MCPT]):
        """Initialize the transformer with model types."""
        self.copper_model = copper_model
        self.mcp_model = mcp_model
        self.entity_type = mcp_model.model_fields["type"].default
    
    def to_mcp(self, data: Union[Dict[str, Any], CopperT]) -> Dict[str, Any]:
        """Transform Copper data to MCP format."""
        # If data is already a model instance, use it directly
        if isinstance(data, self.copper_model):
            validated_data = data
        else:
            validated_data = self.copper_model.model_validate(data)
            
        mcp_data = self._to_mcp_format(validated_data)
        
        # Add standard MCP fields if not already present
        if "type" not in mcp_data:
            mcp_data["type"] = self.entity_type
            
        # Ensure attributes field exists
        if "attributes" not in mcp_data:
            mcp_data["attributes"] = {}
            
        # Add timestamps if available
        if hasattr(validated_data, "date_created"):
            mcp_data["attributes"]["created_at"] = self._format_datetime(validated_data.date_created)
            
        if hasattr(validated_data, "date_modified"):
            mcp_data["attributes"]["updated_at"] = self._format_datetime(validated_data.date_modified)
            
        # Add standard MCP fields
        mcp_data.update({
            "source": "copper",
            "source_id": str(validated_data.id),
            "relationships": mcp_data.get("relationships", {}),
            "meta": mcp_data.get("meta", {})
        })
        
        # Create MCP model instance
        mcp_instance = self.mcp_model.model_validate(mcp_data)
        return mcp_instance.model_dump(exclude_none=True)
    
    def _to_mcp_format(self, data: CopperT) -> Dict[str, Any]:
        """Transform validated Copper data to MCP format.
        
        This method should be implemented by subclasses to handle specific
        transformations for each entity type.
        """
        raise NotImplementedError("Subclasses must implement _to_mcp_format")
    
    def _format_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        """Format a datetime to ISO8601 format with UTC timezone."""
        if dt is None:
            return None
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    def _get_primary_contact(self, contacts: list) -> Optional[str]:
        """Get the primary contact value from a list of contacts."""
        if not contacts:
            return None
            
        # Try to find a work contact first
        for contact in contacts:
            if contact.get("category") == "work":
                return contact["value"]
                
        # Fall back to the first contact
        return contacts[0]["value"]
        
    def _create_relationship(
        self, 
        rel_type: str, 
        rel_id: Optional[int], 
        name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a relationship object in MCP format."""
        if rel_id is None:
            return {"data": None}
        
        rel_data = {
            "type": rel_type,
            "id": str(rel_id)
        }
        
        if name:
            rel_data["name"] = name
            
        return {"data": rel_data}

class TransformationError(Exception):
    """Exception raised for errors during data transformation."""
    
    def __init__(self, message: str, data: Optional[Dict[str, Any]] = None):
        """
        Initialize the error.

        Args:
            message: Error description
            data: Optional data that caused the error
        """
        self.message = message
        self.data = data
        super().__init__(self.message) 