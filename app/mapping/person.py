"""Person transformer for converting Copper person data to MCP format."""
from typing import Dict, Any, List, Union, Optional
from datetime import datetime, timezone

from app.mapping.transform import BaseTransformer
from app.models.copper import Person, EmailPhone, Social, Address, CustomField
from app.models.mcp import MCPPerson

class PersonTransformer(BaseTransformer):
    """Transform Person data between Copper and MCP formats."""

    def __init__(self, copper_model: type[Person], mcp_model: type[MCPPerson]):
        """Initialize the transformer with models."""
        super().__init__(copper_model, mcp_model)
        self.entity_type = "person"

    def _to_mcp_format(self, data: Person) -> Dict[str, Any]:
        """Transform validated Copper Person data to MCP format.
        
        Args:
            data: Validated Person model instance
            
        Returns:
            Dictionary in MCP format
        """
        # Get primary email and phone (prioritize work category)
        primary_email = self._get_primary_contact(data.emails, "work") if data.emails else None
        primary_phone = self._get_primary_contact(data.phone_numbers, "work") if data.phone_numbers else None
        
        # Extract name components or use full name
        name_parts = {
            "prefix": data.prefix,
            "first_name": data.first_name or data.name.split()[0] if data.name else None,
            "last_name": data.last_name or " ".join(data.name.split()[1:]) if data.name and len(data.name.split()) > 1 else None,
            "suffix": data.suffix
        }
        
        result = {
            "id": str(data.id) if data.id else None,
            "type": "person",
            "attributes": {
                "name": data.name,
                **name_parts,
                "title": data.title,
                "company_name": data.company_name,
                "email": primary_email.email if primary_email else None,
                "phone": primary_phone.phone if primary_phone else None,
                "socials": [social.model_dump() for social in data.socials] if data.socials else [],
                "websites": data.websites or [],
                "address": {
                    "street": data.address.street if data.address else None,
                    "city": data.address.city if data.address else None,
                    "state": data.address.state if data.address else None,
                    "postal_code": data.address.postal_code if data.address else None,
                    "country": data.address.country if data.address else None
                } if data.address else None,
                "details": data.details,
                "tags": data.tags or []
            },
            "relationships": {},
            "meta": {
                "custom_fields": {}
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
            result["meta"]["custom_fields"] = {
                str(field.custom_field_definition_id): field.value
                for field in data.custom_fields
            }

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

    def _get_primary_contact(self, contacts: List[EmailPhone], preferred_category: str = "work") -> Optional[EmailPhone]:
        """Get primary contact info, prioritizing work category.
        
        Args:
            contacts: List of contact objects (emails or phones)
            preferred_category: Category to prioritize (default: "work")
            
        Returns:
            Primary contact object or None if no contacts
        """
        if not contacts:
            return None
            
        # First try to find a work contact
        work_contacts = [c for c in contacts if c.category == preferred_category]
        if work_contacts:
            return work_contacts[0]
            
        # If no work contact, return the first one
        return contacts[0]

    def from_copper(self, data: Dict[Any, Any]) -> Person:
        """Transform Copper data to Person model."""
        # Extract primary email and phone from attributes
        attributes = data.get("attributes", {})
        emails = self._parse_contacts(attributes.get("emails", []))
        phones = self._parse_contacts(attributes.get("phone_numbers", []))
        
        # Get address if present
        address_data = attributes.get("address")
        address = None
        if address_data and isinstance(address_data, dict):
            try:
                address = Address(**address_data)
            except (ValueError, TypeError):
                # If address data is invalid, skip it
                pass

        # Get socials if present
        socials_data = attributes.get("socials", [])
        socials = [Social(**social) for social in socials_data] if socials_data else []

        # Get custom fields if present
        custom_fields_data = data.get("custom_fields", [])
        custom_fields = [CustomField(**field) for field in custom_fields_data] if custom_fields_data else []

        return Person(
            id=int(data.get("id")) if data.get("id") else None,
            name=data.get("name"),
            emails=emails,
            phone_numbers=phones,
            socials=socials,
            websites=attributes.get("websites", []),
            address=address,
            assignee_id=int(attributes.get("assignee_id")) if attributes.get("assignee_id") else None,
            contact_type_id=int(attributes.get("contact_type_id")) if attributes.get("contact_type_id") else None,
            details=attributes.get("details"),
            tags=attributes.get("tags", []),
            custom_fields=custom_fields
        )

    def to_copper(self, data: Person) -> Dict[Any, Any]:
        """Transform Person model to Copper format."""
        result = {
            "name": data.name,
            "attributes": {
                "emails": [email.model_dump() for email in data.emails] if data.emails else [],
                "phone_numbers": [phone.model_dump() for phone in data.phone_numbers] if data.phone_numbers else [],
                "socials": [social.model_dump() for social in data.socials] if data.socials else [],
                "websites": data.websites or [],
                "address": data.address.model_dump() if data.address else None,
                "assignee_id": data.assignee_id,
                "contact_type_id": data.contact_type_id,
                "details": data.details or None,
                "tags": data.tags or [],
            },
            "custom_fields": [field.model_dump() for field in data.custom_fields] if data.custom_fields else []
        }
        
        # Include ID if provided
        if data.id:
            result["id"] = data.id
            
        return result

    def _parse_contacts(self, contacts_data: List[Dict[str, Any]]) -> List[EmailPhone]:
        """Parse contact information (emails/phones) from Copper format."""
        if not contacts_data:
            return []
            
        return [EmailPhone(**contact) for contact in contacts_data] 