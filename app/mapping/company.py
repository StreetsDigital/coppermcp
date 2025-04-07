"""Company transformer for converting Copper company data to MCP format."""
from typing import Dict, Any, List
from datetime import datetime

from app.mapping.transform import BaseTransformer
from app.models.copper import Company, EmailPhone

class CompanyTransformer(BaseTransformer[Company]):
    """Transformer for Copper Company entities."""

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
        
        result = {
            "id": str(validated_data.id) if validated_data.id else None,
            "type": "company",
            "attributes": {
                "name": validated_data.name,
                "phone": primary_phone.phone if primary_phone else None,
                "website": str(primary_website) if primary_website else None,
                "industry": validated_data.industry,
                "details": validated_data.details,
                "email_domain": validated_data.email_domain,
                "tags": validated_data.tags,
                "annual_revenue": validated_data.annual_revenue,
                "employee_count": validated_data.employee_count,
                "created_at": validated_data.date_created.isoformat() if validated_data.date_created else None,
                "updated_at": validated_data.date_modified.isoformat() if validated_data.date_modified else None
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
                "contact_type_id": validated_data.contact_type_id,
                "additional_phones": [
                    {"phone": p.phone, "category": p.category}
                    for p in validated_data.phone_numbers[1:] if p.phone  # Skip primary
                ],
                "social_profiles": [
                    {"url": str(s.url), "category": s.category}
                    for s in validated_data.socials
                ],
                "additional_websites": [
                    str(w) for w in validated_data.websites[1:]  # Skip primary
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