"""Activity transformer for converting Copper activity data to MCP format."""
from typing import Dict, Any, Optional
from datetime import datetime

from app.mapping.transform import BaseTransformer
from app.copper.models.activities import Activity, ActivityCreate

class ActivityTransformer(BaseTransformer[Activity]):
    """Transformer for Copper Activity entities."""

    def _validate_data(self, data: Dict[str, Any]) -> Any:
        """
        Validate input data using appropriate model.
        
        Uses ActivityCreate for new activities (no ID) and Activity for existing ones.
        
        Args:
            data: Raw data to validate
            
        Returns:
            Validated model instance
        """
        if "id" in data:
            return self.model_class(**data)
        return ActivityCreate(**data)

    def _to_mcp_format(self, validated_data: Activity) -> Dict[str, Any]:
        """
        Convert Copper Activity data to MCP format.

        Args:
            validated_data: Validated Activity model instance

        Returns:
            Dict[str, Any]: Activity data in MCP format
        """
        def format_datetime(timestamp: Optional[int]) -> Optional[str]:
            """Format Unix timestamp to ISO8601 with 'Z' timezone."""
            if not timestamp:
                return None
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        result = {
            "id": str(validated_data.id) if hasattr(validated_data, "id") else None,
            "type": "activity",
            "attributes": {
                "activity_type": {
                    "category": validated_data.type.category,
                    "id": str(validated_data.type.id)
                },
                "details": validated_data.details,
                "activity_date": format_datetime(validated_data.activity_date),
                "created_at": format_datetime(validated_data.date_created) if hasattr(validated_data, "date_created") else None,
                "updated_at": format_datetime(validated_data.date_modified) if hasattr(validated_data, "date_modified") else None
            },
            "relationships": {
                "parent": {
                    "data": {
                        "type": validated_data.parent.type,
                        "id": str(validated_data.parent.id)
                    }
                },
                "user": {
                    "data": {
                        "type": "user",
                        "id": str(validated_data.user_id)
                    } if validated_data.user_id else None
                },
                "assignee": {
                    "data": {
                        "type": "user",
                        "id": str(validated_data.assignee_id)
                    } if validated_data.assignee_id else None
                }
            },
            "meta": {
                "custom_fields": {
                    str(f.custom_field_definition_id): f.value
                    for f in (validated_data.custom_fields or [])
                }
            }
        }

        return result 