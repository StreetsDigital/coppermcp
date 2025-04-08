"""Company transformer for converting Copper company data to MCP format."""
from typing import Dict, Any, List, TypeVar, Union, Optional
from datetime import datetime, timezone
from pydantic import HttpUrl

from app.mapping.transform import BaseTransformer
from app.models.copper import Company, EmailPhone, Social, Address, CustomField
from app.models.mcp import MCPCompany

class CompanyTransformer(BaseTransformer):
    """Transform Company data between Copper and MCP formats."""

    def __init__(self, copper_model: type[Company], mcp_model: type[MCPCompany]):
        """Initialize the transformer with models."""
        super().__init__(copper_model, mcp_model)
        self.entity_type = "company"

    def _to_mcp_format(self, data: Company) -> Dict[str, Any]:
        """Transform Copper Company to MCP format."""
        # Get primary contact methods
        primary_phone = self._get_primary_contact(data.phone_numbers, "work") if data.phone_numbers else None
        primary_website = data.websites[0] if data.websites else None

        result = {
            "type": self.entity_type,
            "attributes": {
                "name": data.name,
                "email_domain": data.email_domain,
                "details": data.details,
                "industry": data.industry,
                "annual_revenue": data.annual_revenue,
                "employee_count": data.employee_count,
                "status": data.status,
                "phone": primary_phone.phone if primary_phone else None,
                "website": str(primary_website) if primary_website else None,
                "phone_numbers": [
                    {
                        "number": phone.phone,
                        "category": phone.category
                    }
                    for phone in (data.phone_numbers or [])
                ],
                "socials": [
                    {
                        "url": str(social.url),
                        "category": social.category
                    }
                    for social in (data.socials or [])
                ],
                "websites": [str(website) for website in (data.websites or [])],
                "address": {
                    "street": data.address.street if data.address else None,
                    "city": data.address.city if data.address else None,
                    "state": data.address.state if data.address else None,
                    "postal_code": data.address.postal_code if data.address else None,
                    "country": data.address.country if data.address else None
                } if data.address else None,
                "tags": data.tags or []
            },
            "relationships": {},
            "meta": {
                "custom_fields": [],
                "interaction_count": data.interaction_count or 0,
                "created_at": self._format_datetime(data.date_created),
                "updated_at": self._format_datetime(data.date_modified)
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

        # Add primary contact relationship if present
        if data.primary_contact_id:
            result["relationships"]["primary_contact"] = {
                "data": {
                    "type": "person",
                    "id": str(data.primary_contact_id)
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
            "industry": data.attributes.get("industry"),
            "annual_revenue": data.attributes.get("annual_revenue"),
            "employee_count": data.attributes.get("employee_count"),
            "status": data.attributes.get("status"),
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
            "websites": [
                str(website) if isinstance(website, HttpUrl) else website
                for website in data.attributes.get("websites", [])
            ]
        }

        # Add address if present
        address_data = data.attributes.get("address")
        if address_data:
            result["address"] = Address(**address_data).dict(exclude_none=True)

        # Add assignee if present
        if "assignee" in data.relationships:
            result["assignee_id"] = int(data.relationships["assignee"]["data"]["id"])

        # Add primary contact if present
        if "primary_contact" in data.relationships:
            result["primary_contact_id"] = int(data.relationships["primary_contact"]["data"]["id"])

        # Add custom fields if present
        if data.meta and "custom_fields" in data.meta:
            result["custom_fields"] = [
                {
                    "custom_field_definition_id": int(field["id"]),
                    "value": field["value"]
                }
                for field in data.meta["custom_fields"]
            ]

        # Add tags if present
        if "tags" in data.attributes:
            result["tags"] = data.attributes["tags"]

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

    def _format_datetime(self, dt: Optional[Union[datetime, int]]) -> Optional[str]:
        """Format a datetime or Unix timestamp to ISO8601 format with UTC timezone.
        
        Args:
            dt: Either a datetime object or Unix timestamp (int)
            
        Returns:
            ISO8601 formatted string or None if input is None
        """
        if dt is None:
            return None
            
        if isinstance(dt, int):
            dt = datetime.fromtimestamp(dt, timezone.utc)
            
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ") 