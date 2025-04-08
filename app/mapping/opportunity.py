"""Opportunity transformer for converting Copper opportunity data to MCP format."""
from typing import Dict, Any, List
from datetime import datetime

from app.mapping.transform import BaseTransformer
from app.models.copper import Opportunity
from app.models.mcp import MCPOpportunity

class OpportunityTransformer(BaseTransformer[Opportunity, MCPOpportunity]):
    """Transformer for Copper Opportunity entities."""

    def __init__(self, copper_model: type[Opportunity], mcp_model: type[MCPOpportunity]):
        """Initialize the transformer."""
        super().__init__(copper_model=copper_model, mcp_model=mcp_model)

    def _to_mcp_format(self, validated_data: Opportunity) -> Dict[str, Any]:
        """
        Convert Copper Opportunity data to MCP format.

        Args:
            validated_data: Validated Opportunity model instance

        Returns:
            Dict[str, Any]: Opportunity data in MCP format
        """
        result = {
            "type": "opportunity",
            "attributes": {
                "name": validated_data.name,
                "status": validated_data.status,
                "priority": validated_data.priority,
                "monetary_value": validated_data.monetary_value,
                "win_probability": validated_data.win_probability,
                "close_date": self._format_datetime(validated_data.close_date),
                "details": validated_data.details,
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
                "company": {
                    "data": {
                        "type": "company",
                        "id": str(validated_data.company_id),
                        "name": validated_data.company_name
                    } if validated_data.company_id else None
                },
                "primary_contact": {
                    "data": {
                        "type": "person",
                        "id": str(validated_data.primary_contact_id)
                    } if validated_data.primary_contact_id else None
                }
            },
            "meta": {
                "interaction_count": validated_data.interaction_count or 0,
                "pipeline_id": validated_data.pipeline_id,
                "pipeline_stage_id": validated_data.pipeline_stage_id,
                "custom_fields": {
                    str(f.custom_field_definition_id): f.value
                    for f in validated_data.custom_fields
                }
            }
        }
        
        return result 