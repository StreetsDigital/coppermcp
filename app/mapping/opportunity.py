"""Opportunity transformer for converting Copper opportunity data to MCP format."""
from typing import Dict, Any, List
from datetime import datetime

from app.mapping.transform import BaseTransformer
from app.models.copper import Opportunity
from app.models.mcp import MCPOpportunity

class OpportunityTransformer(BaseTransformer):
    """Transform Opportunity data between Copper and MCP formats."""

    def __init__(self, copper_model: type[Opportunity], mcp_model: type[MCPOpportunity]):
        """Initialize the transformer with models."""
        super().__init__(copper_model, mcp_model)
        self.entity_type = "opportunity"

    def _to_mcp_format(self, data: Opportunity) -> Dict[str, Any]:
        """Transform Copper Opportunity to MCP format."""
        result = {
            "type": self.entity_type,
            "attributes": {
                "name": data.name,
                "status": data.status,
                "pipeline_id": str(data.pipeline_id),
                "pipeline_stage_id": str(data.pipeline_stage_id),
                "details": data.details,
                "monetary_value": data.monetary_value,
                "win_probability": data.win_probability,
                "close_date": data.close_date
            },
            "relationships": {},
            "meta": {
                "custom_fields": []
            }
        }

        # Add company relationship if present
        if data.company_id:
            result["relationships"]["company"] = {
                "data": {
                    "type": "company",
                    "id": str(data.company_id)
                }
            }

        # Add primary contact relationship if present
        if data.primary_contact_id:
            result["relationships"]["primary_contact"] = {
                "data": {
                    "type": "person",
                    "id": str(data.primary_contact_id)
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

    def _to_copper_format(self, data: MCPOpportunity) -> Dict[str, Any]:
        """Transform MCP Opportunity to Copper format."""
        result = {
            "name": data.attributes.get("name"),
            "status": data.attributes.get("status"),
            "pipeline_id": int(data.attributes.get("pipeline_id")),
            "pipeline_stage_id": int(data.attributes.get("pipeline_stage_id")),
            "details": data.attributes.get("details"),
            "monetary_value": data.attributes.get("monetary_value"),
            "win_probability": data.attributes.get("win_probability"),
            "close_date": data.attributes.get("close_date")
        }

        # Add company if present
        if "company" in data.relationships:
            result["company_id"] = int(data.relationships["company"]["data"]["id"])

        # Add primary contact if present
        if "primary_contact" in data.relationships:
            result["primary_contact_id"] = int(data.relationships["primary_contact"]["data"]["id"])

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