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

    def _to_mcp_format(self, validated_data: Activity) -> Dict[str, Any]:
        """
        Convert Copper Activity data to MCP format.

        Args:
            validated_data: Validated Activity model instance

        Returns:
            Dict[str, Any]: Activity data in MCP format
        """
        result = {
            "type": "activity",
            "attributes": {
                "name": validated_data.details,  # Use details as name
                "details": validated_data.details,
                "activity_type": {
                    "id": str(validated_data.type.id),  # Convert ID to string
                    "category": validated_data.type.category
                },
                "activity_date": self._format_datetime(validated_data.activity_date),
                "tags": validated_data.tags or [],
                "created_at": self._format_datetime(validated_data.date_created),
                "updated_at": self._format_datetime(validated_data.date_modified)
            },
            "relationships": {
                "assignee": {
                    "data": {
                        "type": "user",
                        "id": str(validated_data.assignee_id)
                    } if validated_data.assignee_id else None
                },
                "parent": self._get_parent_relationship(validated_data)
            },
            "meta": {
                "custom_fields": {
                    str(f.custom_field_definition_id): f.value
                    for f in validated_data.custom_fields
                }
            }
        }
        
        return result

    def _get_parent_relationship(self, activity: Activity) -> Dict[str, Any]:
        """Get the parent relationship data for an activity.
        
        Args:
            activity: Activity model instance
            
        Returns:
            Dict[str, Any]: Parent relationship data
        """
        if not activity.parent:
            return {"data": None}
            
        return {
            "data": {
                "type": activity.parent.type.lower(),
                "id": str(activity.parent.id)
            }
        }

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