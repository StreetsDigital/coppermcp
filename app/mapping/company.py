"""Company transformer for converting Copper company data to MCP format."""
from typing import Dict, Any, List, TypeVar, Union
from datetime import datetime

from app.mapping.transform import BaseTransformer
from app.models.copper import Company, EmailPhone
from app.models.mcp import MCPCompany

class CompanyTransformer(BaseTransformer):
    """Transform Company data between Copper and MCP formats."""

    def __init__(self, copper_model: type[Company], mcp_model: type[MCPCompany]):
        """Initialize the transformer with models."""
        super().__init__(copper_model, mcp_model)
        self.entity_type = "company"

    def _to_mcp_format(self, data: Company) -> Dict[str, Any]:
        """Transform Copper Company to MCP format."""
        result = {
            "type": self.entity_type,
            "attributes": {
                "name": data.name,
                "email_domain": data.email_domain,
                "details": data.details,
                "phone_numbers": [
                    {
                        "number": phone.number,
                        "category": phone.category
                    }
                    for phone in (data.phone_numbers or [])
                ],
                "socials": [
                    {
                        "url": social.url,
                        "category": social.category
                    }
                    for social in (data.socials or [])
                ],
                "websites": [str(website) for website in (data.websites or [])]
            },
            "relationships": {},
            "meta": {
                "custom_fields": []
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

    def _to_copper_format(self, data: MCPCompany) -> Dict[str, Any]:
        """Transform MCP Company to Copper format."""
        result = {
            "name": data.attributes.get("name"),
            "email_domain": data.attributes.get("email_domain"),
            "details": data.attributes.get("details"),
            "phone_numbers": [
                {
                    "number": phone["number"],
                    "category": phone["category"]
                }
                for phone in data.attributes.get("phone_numbers", [])
            ],
            "socials": [
                {
                    "url": social["url"],
                    "category": social["category"]
                }
                for social in data.attributes.get("socials", [])
            ],
            "websites": data.attributes.get("websites", [])
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

    def _get_primary_contact(self, contacts: List[EmailPhone]) -> str:
        """Get the primary contact method value (first in list or work category).
        
        Args:
            contacts: List of contact methods
            
        Returns:
            str: Primary contact value or None if no contacts
        """
        if not contacts:
            return None
            
        # First try to find a work contact
        work_contact = next(
            (c for c in contacts if c.category.lower() == "work"),
            None
        )
        
        # If no work contact, use the first one
        contact = work_contact or contacts[0]
        
        # Return phone value
        return contact.phone if contact else None 