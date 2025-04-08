"""Person transformer for converting Copper person data to MCP format."""
from typing import Dict, Any, List
from datetime import datetime

from app.mapping.transform import BaseTransformer
from app.models.copper import Person, EmailPhone
from app.models.mcp import MCPPerson

class PersonTransformer(BaseTransformer[Person, MCPPerson]):
    """Transformer for Copper Person entities."""
    
    def __init__(self, copper_model: type[Person], mcp_model: type[MCPPerson]):
        """Initialize the transformer."""
        super().__init__(copper_model=copper_model, mcp_model=mcp_model)

    def _to_mcp_format(self, validated_data: Person) -> Dict[str, Any]:
        """
        Convert Copper Person data to MCP format.

        Args:
            validated_data: Validated Person model instance

        Returns:
            Dict[str, Any]: Person data in MCP format
        """
        result = {
            "type": "person",
            "attributes": {
                "name": validated_data.name,
                "first_name": validated_data.first_name,
                "last_name": validated_data.last_name,
                "title": validated_data.title,
                "email": self._get_primary_contact(validated_data.emails) if validated_data.emails else None,
                "phone": self._get_primary_contact(validated_data.phone_numbers) if validated_data.phone_numbers else None,
                "details": validated_data.details,
                "tags": validated_data.tags,
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
                }
            },
            "meta": {
                "interaction_count": validated_data.interaction_count or 0,
                "contact_type_id": validated_data.contact_type_id,
                "custom_fields": {
                    str(f.custom_field_definition_id): f.value
                    for f in validated_data.custom_fields
                }
            }
        }
        
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