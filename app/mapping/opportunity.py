"""Opportunity transformer for converting Copper opportunity data to MCP format."""
from typing import Dict, Any, Optional
from datetime import datetime

from app.mapping.transform import BaseTransformer
from app.models.copper import Opportunity

class OpportunityTransformer(BaseTransformer[Opportunity]):
    """Transformer for Copper Opportunity entities."""

    def _to_mcp_format(self, validated_data: Opportunity) -> Dict[str, Any]:
        """
        Convert Copper Opportunity data to MCP format.

        Args:
            validated_data: Validated Opportunity model instance

        Returns:
            Dict[str, Any]: Opportunity data in MCP format
        """
        def format_datetime(dt: Optional[datetime]) -> Optional[str]:
            """Format datetime to ISO8601 with 'Z' timezone."""
            if not dt:
                return None
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        result = {
            "id": str(validated_data.id) if validated_data.id else None,
            "type": "opportunity",
            "attributes": {
                "name": validated_data.name,
                "status": validated_data.status,
                "priority": validated_data.priority,
                "monetary_value": validated_data.monetary_value,
                "win_probability": validated_data.win_probability,
                "details": validated_data.details,
                "close_date": format_datetime(validated_data.close_date),
                "tags": validated_data.tags,
                "created_at": format_datetime(validated_data.date_created),
                "updated_at": format_datetime(validated_data.date_modified)
            },
            "relationships": {
                "assignee": {
                    "data": {
                        "type": "user",
                        "id": str(validated_data.assignee_id)
                    } if validated_data.assignee_id else None
                },
                "company": {
                    "data": {
                        "type": "company",
                        "id": str(validated_data.company_id),
                        "name": validated_data.company_name
                    } if validated_data.company_id else None
                },
                "pipeline": {
                    "data": {
                        "type": "pipeline",
                        "id": str(validated_data.pipeline_id)
                    } if validated_data.pipeline_id else None
                },
                "pipeline_stage": {
                    "data": {
                        "type": "pipeline_stage",
                        "id": str(validated_data.pipeline_stage_id)
                    } if validated_data.pipeline_stage_id else None
                }
            },
            "meta": {
                "interaction_count": validated_data.interaction_count or 0,
                "custom_fields": {
                    str(f.custom_field_definition_id): f.value
                    for f in validated_data.custom_fields
                }
            }
        }

        return result 