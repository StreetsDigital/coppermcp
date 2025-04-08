"""Activity transformer for converting Copper activity data to MCP format."""
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timezone

from app.mapping.transform import BaseTransformer
from app.models.copper import Activity, ActivityType, CustomField
from app.models.mcp import MCPActivity

class ActivityTransformer(BaseTransformer):
    """Transformer for Activity entities between Copper CRM and MCP."""

    def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform a Copper activity into MCP format.
        
        Args:
            data: Activity data from Copper CRM
            
        Returns:
            Transformed activity data for MCP
            
        Raises:
            ValueError: If required fields are missing
        """
        if not data:
            raise ValueError("Activity data cannot be empty")

        activity_type = ActivityType(
            id=str(data.get("activity_type", {}).get("id", "")),
            category=data.get("activity_type", {}).get("category", ""),
            name=data.get("activity_type", {}).get("name", "")
        )

        custom_fields = []
        for field in data.get("custom_fields", []):
            custom_fields.append(CustomField(
                id=str(field.get("custom_field_definition_id", "")),
                value=field.get("value", "")
            ))

        activity = Activity(
            id=str(data.get("id", "")),
            type=activity_type,
            details=data.get("details", ""),
            activity_date=int(data.get("activity_date", 0)),
            user_id=str(data.get("user_id", "")),
            parent={
                "type": data.get("parent", {}).get("type", ""),
                "id": str(data.get("parent", {}).get("id", ""))
            },
            assignee_id=str(data.get("assignee_id", "")) if data.get("assignee_id") else None,
            custom_fields=custom_fields,
            created_at=int(data.get("created_at", 0)),
            updated_at=int(data.get("updated_at", 0))
        )

        return activity.dict(exclude_none=True)

    def reverse_transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform MCP activity data into Copper CRM format.
        
        Args:
            data: Activity data from MCP
            
        Returns:
            Transformed activity data for Copper CRM
            
        Raises:
            ValueError: If required fields are missing
        """
        if not data:
            raise ValueError("Activity data cannot be empty")

        activity_type = data.get("type", {})
        
        copper_data = {
            "activity_type": {
                "id": int(activity_type.get("id", 0)),
                "category": activity_type.get("category", ""),
                "name": activity_type.get("name", "")
            },
            "details": data.get("details", ""),
            "activity_date": data.get("activity_date", 0),
            "user_id": int(data.get("user_id", 0)),
            "parent": {
                "type": data.get("parent", {}).get("type", ""),
                "id": int(data.get("parent", {}).get("id", 0))
            }
        }

        if data.get("assignee_id"):
            copper_data["assignee_id"] = int(data["assignee_id"])

        if data.get("custom_fields"):
            copper_data["custom_fields"] = [
                {
                    "custom_field_definition_id": int(field["id"]),
                    "value": field["value"]
                }
                for field in data["custom_fields"]
            ]

        return copper_data

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