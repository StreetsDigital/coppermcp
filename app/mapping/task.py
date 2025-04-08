"""Task transformer for converting between Copper and MCP formats."""
from typing import Dict, Any, Optional
from datetime import datetime

from app.models.copper import Task
from app.models.mcp import MCPTask
from app.mapping.transform import BaseTransformer


class TaskTransformer(BaseTransformer):
    """Transform Task data between Copper and MCP formats."""

    def __init__(self, copper_model: type[Task], mcp_model: type[MCPTask]):
        """Initialize the transformer with models."""
        super().__init__(copper_model, mcp_model)
        self.entity_type = "task"

    def _to_mcp_format(self, data: Task) -> Dict[str, Any]:
        """Transform Copper Task to MCP format."""
        result = {
            "type": self.entity_type,
            "id": str(data.id) if data.id else "0",  # Default ID if none provided
            "attributes": {
                "name": data.name,
                "details": data.details,
                "status": data.status,
                "priority": data.priority,
                "due_date": data.due_date,
                "reminder_date": data.reminder_date,
                "completed_date": data.completed_date
            },
            "relationships": {},
            "meta": {
                "custom_fields": []
            }
        }

        # Add related resource relationship if present
        if data.related_resource:
            result["relationships"]["related_resource"] = {
                "data": {
                    "type": data.related_resource.type,
                    "id": str(data.related_resource.id)
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

    def _to_copper_format(self, data: MCPTask) -> Dict[str, Any]:
        """Transform MCP Task to Copper format."""
        result = {
            "name": data.attributes.get("name"),
            "details": data.attributes.get("details"),
            "status": data.attributes.get("status"),
            "priority": data.attributes.get("priority"),
            "due_date": data.attributes.get("due_date"),
            "reminder_date": data.attributes.get("reminder_date"),
            "completed_date": data.attributes.get("completed_date")
        }

        # Add related resource if present
        if "related_resource" in data.relationships:
            related = data.relationships["related_resource"]["data"]
            result["related_resource"] = {
                "type": related["type"],
                "id": int(related["id"])
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