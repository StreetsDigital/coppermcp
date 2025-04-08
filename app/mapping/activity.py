"""Activity transformer for converting Copper activity data to MCP format."""
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timezone

from app.mapping.transform import BaseTransformer
from app.models.copper import Activity, ActivityCreate
from app.models.mcp import MCPActivity

class ActivityTransformer(BaseTransformer[Activity, MCPActivity]):
    """Transformer for Copper Activity entities."""

    def __init__(self, copper_model: type[Activity], mcp_model: type[MCPActivity]):
        """Initialize the transformer."""
        super().__init__(copper_model=copper_model, mcp_model=mcp_model)
        self.entity_type = "activity"

    def _to_mcp_format(self, data: Activity) -> Dict[str, Any]:
        """Transform Copper Activity to MCP format."""
        result = {
            "type": self.entity_type,
            "attributes": {
                "details": data.details,
                "activity_type": data.type.category if data.type else None,
                "activity_date": data.activity_date
            },
            "relationships": {},
            "meta": {
                "custom_fields": []
            }
        }

        # Add parent relationship if present
        if data.parent:
            result["relationships"]["parent"] = {
                "data": {
                    "type": data.parent.type,
                    "id": str(data.parent.id)
                }
            }

        # Add assignee relationship if present
        if data.assignee_id:
            result["relationships"]["assignee"] = {
                "data": {
                    "type": "user",
                    "id": str(data.assignee_id)
                }
            }

        # Add custom fields if present
        if data.custom_fields:
            result["meta"]["custom_fields"] = [
                {
                    "id": str(field.custom_field_definition_id),
                    "value": field.value
                }
                for field in data.custom_fields
            ]

        return result

    def _to_copper_format(self, data: MCPActivity) -> Dict[str, Any]:
        """Transform MCP Activity to Copper format."""
        result = {
            "details": data.attributes.get("details"),
            "type": {
                "category": data.attributes.get("activity_type"),
                "id": "123"  # Default ID for user activity type
            },
            "activity_date": data.attributes.get("activity_date")
        }

        # Add parent relationship if present
        if "parent" in data.relationships:
            parent = data.relationships["parent"]["data"]
            result["parent"] = {
                "type": parent["type"],
                "id": int(parent["id"])
            }

        # Add assignee if present
        if "assignee" in data.relationships:
            result["assignee_id"] = int(data.relationships["assignee"]["data"]["id"])

        # Add custom fields if present
        if data.meta and "custom_fields" in data.meta:
            result["custom_fields"] = [
                {
                    "custom_field_definition_id": int(field["id"]),
                    "value": field["value"]
                }
                for field in data.meta["custom_fields"]
            ]

        return result

    def _validate_data(self, data: Dict[str, Any]) -> Activity:
        """
        Validate input data using appropriate model.
        
        Uses ActivityCreate for new activities (no ID) and Activity for existing ones.
        
        Args:
            data: Raw data to validate
            
        Returns:
            Activity: Validated model instance
        """
        if "id" in data:
            return Activity(**data)
        return ActivityCreate(**data)

    def _format_datetime(self, timestamp: Optional[Union[int, datetime]]) -> Optional[str]:
        """
        Format Unix timestamp or datetime to ISO8601 with 'Z' timezone.
        
        Args:
            timestamp: Unix timestamp in seconds or datetime object
            
        Returns:
            Optional[str]: ISO8601 formatted datetime string or None if timestamp is None
        """
        if not timestamp:
            return None
        if isinstance(timestamp, (int, float)):
            dt = datetime.fromtimestamp(timestamp, timezone.utc)
        else:
            dt = timestamp
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ") 