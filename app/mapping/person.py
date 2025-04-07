"""Person transformer for converting Copper person data to MCP format."""
from typing import Dict, Any, List
from datetime import datetime

from app.mapping.transform import BaseTransformer
from app.models.copper import Person, EmailPhone
from app.models.mcp import MCPPerson

class PersonTransformer(BaseTransformer[Person, MCPPerson]):
    """Transformer for Copper Person entities."""
    
    def __init__(self):
        """Initialize the transformer with models."""
        super().__init__(copper_model=Person, mcp_model=MCPPerson)

    def _to_mcp_format(self, validated_data: Person) -> Dict[str, Any]:
        """
        Convert Copper Person data to MCP format.

        Args:
            validated_data: Validated Person model instance

        Returns:
            Dict[str, Any]: Person data in MCP format
        """
        # Extract primary email and phone
        primary_email = self._get_primary_contact(validated_data.emails)
        primary_phone = self._get_primary_contact(validated_data.phone_numbers)
        
        # Build name components
        name_parts = []
        if validated_data.prefix:
            name_parts.append(validated_data.prefix)
        if validated_data.first_name:
            name_parts.append(validated_data.first_name)
        if validated_data.last_name:
            name_parts.append(validated_data.last_name)
        if validated_data.suffix:
            name_parts.append(validated_data.suffix)
        
        # If no name parts, use full name
        full_name = " ".join(name_parts) if name_parts else validated_data.name
        
        result = {
            "id": str(validated_data.id) if validated_data.id else None,
            "attributes": {
                "name": full_name,
                "first_name": validated_data.first_name,
                "last_name": validated_data.last_name,
                "email": primary_email.email if primary_email else None,
                "phone": primary_phone.phone if primary_phone else None,
                "title": validated_data.title,
                "company": validated_data.company_name,
                "details": validated_data.details,
                "tags": validated_data.tags or []
            },
            "relationships": {
                "company": self._create_relationship(
                    "company",
                    validated_data.company_id,
                    validated_data.company_name
                ),
                "assignee": self._create_relationship(
                    "user",
                    validated_data.assignee_id
                )
            },
            "meta": {
                "interaction_count": validated_data.interaction_count or 0,
                "contact_type_id": validated_data.contact_type_id,
                "additional_emails": [
                    {"email": e.email, "category": e.category}
                    for e in validated_data.emails[1:] if e.email  # Skip primary
                ],
                "additional_phones": [
                    {"phone": p.phone, "category": p.category}
                    for p in validated_data.phone_numbers[1:] if p.phone  # Skip primary
                ],
                "social_profiles": [
                    {"url": str(s.url), "category": s.category}
                    for s in validated_data.socials
                ],
                "websites": [str(w) for w in validated_data.websites],
                "custom_fields": {
                    str(f.custom_field_definition_id): f.value
                    for f in validated_data.custom_fields
                }
            }
        }
        
        # Add address if present
        if validated_data.address:
            result["attributes"]["address"] = {
                "street": validated_data.address.street,
                "city": validated_data.address.city,
                "state": validated_data.address.state,
                "postal_code": validated_data.address.postal_code,
                "country": validated_data.address.country
            }
        
        return result

    def _get_primary_contact(self, contacts: List[EmailPhone]) -> EmailPhone:
        """Get the primary contact method (first in list or work category)."""
        if not contacts:
            return None
            
        # First try to find a work contact
        work_contact = next(
            (c for c in contacts if c.category.lower() == "work"),
            None
        )
        
        # If no work contact, use the first one
        return work_contact or contacts[0] 