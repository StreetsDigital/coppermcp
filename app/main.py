"""Main FastAPI application module for Copper MCP Server.

This module provides the FastAPI application and endpoints for the Copper MCP Server.
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List, Optional
import os

from .copper.client.base import CopperClient
from .copper.auth import get_auth_token
from .copper.client.people import PeopleClient
from .copper.client.companies import CompaniesClient
from .copper.client.opportunities import OpportunitiesClient
from .copper.client.activities import ActivitiesClient
from .copper.client.tasks import TasksClient

from .mapping.person import PersonTransformer
from .mapping.company import CompanyTransformer
from .mapping.opportunity import OpportunityTransformer
from .mapping.activity import ActivityTransformer

# Create FastAPI app
app = FastAPI(
    title="Copper MCP Server",
    description="Model Context Protocol implementation for Copper CRM",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize transformers
person_transformer = PersonTransformer()
company_transformer = CompanyTransformer()
opportunity_transformer = OpportunityTransformer()
activity_transformer = ActivityTransformer()

async def get_copper_client() -> CopperClient:
    """Get a configured Copper client.
    
    Returns:
        CopperClient: Configured client instance
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        token = get_auth_token()
        return CopperClient(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "copper-mcp",
        "version": "0.1.0"
    }

@app.get("/search")
async def search(
    query: str,
    entity_type: Optional[str] = None,
    client: CopperClient = Depends(get_copper_client)
) -> List[Dict[str, Any]]:
    """Search across Copper entities.
    
    Args:
        query: Search query string
        entity_type: Optional entity type to filter by
        client: Copper client from dependency
        
    Returns:
        List[Dict[str, Any]]: Search results in MCP format
    """
    results = []
    search_query = {"query": query}
    
    # Create entity clients
    people_client = PeopleClient(client)
    companies_client = CompaniesClient(client)
    opportunities_client = OpportunitiesClient(client)
    activities_client = ActivitiesClient(client)
    
    try:
        # Search people
        if not entity_type or entity_type == "person":
            people = await people_client.search(search_query)
            results.extend([
                person_transformer.to_mcp(person)
                for person in people
            ])
            
        # Search companies
        if not entity_type or entity_type == "company":
            companies = await companies_client.search(search_query)
            results.extend([
                company_transformer.to_mcp(company)
                for company in companies
            ])
            
        # Search opportunities
        if not entity_type or entity_type == "opportunity":
            opportunities = await opportunities_client.search(search_query)
            results.extend([
                opportunity_transformer.to_mcp(opp)
                for opp in opportunities
            ])
            
        # Search activities
        if not entity_type or entity_type == "activity":
            activities = await activities_client.search(search_query)
            results.extend([
                activity_transformer.to_mcp(activity)
                for activity in activities
            ])
            
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/people/{person_id}")
async def get_person(
    person_id: int,
    client: CopperClient = Depends(get_copper_client)
) -> Dict[str, Any]:
    """Get a person by ID.
    
    Args:
        person_id: Person ID
        client: Copper client from dependency
        
    Returns:
        Dict[str, Any]: Person data in MCP format
    """
    try:
        people_client = PeopleClient(client)
        person = await people_client.get(person_id)
        return person_transformer.to_mcp(person)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/companies/{company_id}")
async def get_company(
    company_id: int,
    client: CopperClient = Depends(get_copper_client)
) -> Dict[str, Any]:
    """Get a company by ID.
    
    Args:
        company_id: Company ID
        client: Copper client from dependency
        
    Returns:
        Dict[str, Any]: Company data in MCP format
    """
    try:
        companies_client = CompaniesClient(client)
        company = await companies_client.get(company_id)
        return company_transformer.to_mcp(company)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/opportunities/{opportunity_id}")
async def get_opportunity(
    opportunity_id: int,
    client: CopperClient = Depends(get_copper_client)
) -> Dict[str, Any]:
    """Get an opportunity by ID.
    
    Args:
        opportunity_id: Opportunity ID
        client: Copper client from dependency
        
    Returns:
        Dict[str, Any]: Opportunity data in MCP format
    """
    try:
        opportunities_client = OpportunitiesClient(client)
        opportunity = await opportunities_client.get(opportunity_id)
        return opportunity_transformer.to_mcp(opportunity)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/activities/{activity_id}")
async def get_activity(
    activity_id: int,
    client: CopperClient = Depends(get_copper_client)
) -> Dict[str, Any]:
    """Get an activity by ID.
    
    Args:
        activity_id: Activity ID
        client: Copper client from dependency
        
    Returns:
        Dict[str, Any]: Activity data in MCP format
    """
    try:
        activities_client = ActivitiesClient(client)
        activity = await activities_client.get(activity_id)
        return activity_transformer.to_mcp(activity)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e)) 