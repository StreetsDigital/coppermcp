"""Company transformer for converting Copper company data to MCP format."""
from typing import Dict, Any, List, TypeVar
from datetime import datetime

from app.mapping.transform import BaseTransformer
from app.models.copper import Company, EmailPhone
from app.models.mcp import MCPCompany

class CompanyTransformer(BaseTransformer[Company, MCPCompany]):
    """Transformer for Copper Company entities."""
    
    def __init__(self, copper_model: type[Company], mcp_model: type[MCPCompany]):
        """Initialize the transformer with models."""
        super().__init__(copper_model=copper_model, mcp_model=mcp_model)

    def _to_mcp_format(self, validated_data: Company) -> Dict[str, Any]:
        """
        Convert Copper Company data to MCP format.

        Args:
            validated_data: Validated Company model instance

        Returns:
            Dict[str, Any]: Company data in MCP format
        """
        # Extract primary phone
        primary_phone = self._get_primary_contact(validated_data.phone_numbers)
        
        # Get primary website
        primary_website = next(iter(validated_data.websites), None)
        if primary_website:
            primary_website = str(primary_website)  # Convert HttpUrl to string
        
        result = {
            "type": "company",
            "attributes": {
                "name": validated_data.name,
                "phone": primary_phone,
                "website": primary_website,
                "industry": validated_data.industry,
                "details": validated_data.details,
                "email_domain": validated_data.email_domain,
                "tags": validated_data.tags or [],
                "annual_revenue": validated_data.annual_revenue,
                "employee_count": validated_data.employee_count,
                "created_at": self._format_datetime(validated_data.date_created),
                "updated_at": self._format_datetime(validated_data.date_modified)
            },
            "relationships": {
                "assignee": {
                    "data": {
                        "type": "user",
                        "id": str(validated_data.assignee_id)
                    } if validated_data.assignee_id else None
                }
            },
            "meta": {
                "interaction_count": validated_data.interaction_count or 0,
                "additional_phones": [
                    {"phone": p.phone, "category": p.category}
                    for i, p in enumerate(validated_data.phone_numbers)
                    if i > 0 and p.phone  # Skip primary
                ],
                "social_profiles": [
                    {"url": str(s.url), "category": s.category}
                    for s in getattr(validated_data, 'socials', [])
                ],
                "additional_websites": [
                    str(w) for i, w in enumerate(validated_data.websites)  # Convert HttpUrl to string
                    if i > 0  # Skip primary
                ],
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