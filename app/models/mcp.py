"""MCP (Model Context Protocol) data models.

This module defines the Pydantic models for MCP format data structures.
These models ensure consistent data validation and serialization across
different entity types.
"""
from typing import Dict, Any, Optional, List, Union, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class MCPRelationshipData(BaseModel):
    """Data structure for MCP relationships."""
    type: str = Field(..., description="Type of the related entity")
    id: str = Field(..., description="ID of the related entity")
    name: Optional[str] = Field(None, description="Optional name of the related entity")


class MCPRelationship(BaseModel):
    """Structure for a single relationship in MCP format."""
    data: Optional[MCPRelationshipData] = Field(
        None,
        description="Relationship data, null if no relationship exists"
    )


class MCPAttributes(BaseModel):
    """Base attributes for MCP entities."""
    name: Optional[str] = None
    details: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    created_at: Optional[str] = Field(
        None,
        description="ISO8601 timestamp with Z timezone"
    )
    updated_at: Optional[str] = Field(
        None,
        description="ISO8601 timestamp with Z timezone"
    )


class MCPMeta(BaseModel):
    """Metadata for MCP entities."""
    custom_fields: Dict[str, Any] = Field(
        default_factory=dict,
        description="Custom field values keyed by field ID"
    )
    interaction_count: Optional[int] = Field(
        0,
        description="Number of interactions with this entity"
    )


class MCPBase(BaseModel):
    """Base MCP entity model."""
    id: Optional[str] = Field(None, description="Entity ID")
    type: str = Field(..., description="Entity type")
    source: str = Field(..., description="Source system identifier")
    source_id: str = Field(..., description="ID from the source system")
    attributes: MCPAttributes
    relationships: Dict[str, MCPRelationship] = Field(default_factory=dict)
    meta: MCPMeta = Field(default_factory=MCPMeta)


class MCPPersonAttributes(MCPAttributes):
    """Person-specific MCP attributes."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    address: Optional[Dict[str, str]] = None


class MCPCompanyAttributes(MCPAttributes):
    """Company-specific MCP attributes."""
    phone: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    email_domain: Optional[str] = None
    annual_revenue: Optional[float] = None
    employee_count: Optional[int] = None


class MCPOpportunityAttributes(MCPAttributes):
    """Opportunity-specific MCP attributes."""
    status: Optional[str] = None
    priority: Optional[str] = None
    monetary_value: Optional[float] = None
    win_probability: Optional[float] = None
    close_date: Optional[str] = None


class MCPActivityAttributes(MCPAttributes):
    """Activity-specific MCP attributes."""
    activity_type: Dict[str, str] = Field(
        ...,
        description="Activity type information with category and ID"
    )
    activity_date: Optional[str] = Field(
        None,
        description="ISO8601 timestamp of the activity"
    )


class MCPPerson(MCPBase):
    """MCP Person entity."""
    type: Literal["person"]
    attributes: MCPPersonAttributes


class MCPCompany(MCPBase):
    """MCP Company entity."""
    type: Literal["company"]
    attributes: MCPCompanyAttributes


class MCPOpportunity(MCPBase):
    """MCP Opportunity entity."""
    type: Literal["opportunity"]
    attributes: MCPOpportunityAttributes


class MCPActivity(MCPBase):
    """MCP Activity entity."""
    type: Literal["activity"]
    attributes: MCPActivityAttributes 