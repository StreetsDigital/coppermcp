"""Person transformer for converting Copper person data to MCP format."""
from typing import Dict, Any, List, Union
from datetime import datetime

from app.mapping.transform import BaseTransformer
from app.models.copper import Person, EmailPhone
from app.models.mcp import MCPPerson

class PersonTransformer(BaseTransformer):
    """Transform Person data between Copper and MCP formats."""

    def __init__(self, copper_model: type[Person], mcp_model: type[MCPPerson]):
        """Initialize the transformer with models."""
        super().__init__(copper_model, mcp_model)
        self.entity_type = "person"

    def _to_mcp_format(self, data: Person) -> Dict[str, Any]:
        """Transform Copper Person to MCP format."""
        result = {
            "type": self.entity_type,
            "attributes": {
                "name": data.name,
                "email": data.email,
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

        # Add company relationship if present
        if data.company_id:
            result["relationships"]["company"] = {
                "data": {
                    "type": "company",
                    "id": str(data.company_id)
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

    def _to_copper_format(self, data: MCPPerson) -> Dict[str, Any]:
        """Transform MCP Person to Copper format."""
        result = {
            "name": data.attributes.get("name"),
            "email": data.attributes.get("email"),
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

        # Add company if present
        if "company" in data.relationships:
            result["company_id"] = int(data.relationships["company"]["data"]["id"])

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
        
        # Return email or phone value
        return contact.email if hasattr(contact, 'email') and contact.email else contact.phone 