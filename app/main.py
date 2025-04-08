"""Main FastAPI application module for Copper MCP Server.

This module provides the FastAPI application and endpoints for the Copper MCP Server.
It handles routing, authentication, and data transformation between Copper and MCP formats.
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List, Optional, TypeVar, Union
import logging
import os

from .copper.client.base import CopperClient, CopperAPIError
from .copper.auth import get_auth_token, AuthenticationError
from .copper.client.people import PeopleClient
from .copper.client.companies import CompaniesClient
from .copper.client.opportunities import OpportunitiesClient
from .copper.client.activities import ActivitiesClient
from .copper.client.tasks import TasksClient

from .mapping.person import PersonTransformer
from .mapping.company import CompanyTransformer
from .mapping.opportunity import OpportunityTransformer
from .mapping.activity import ActivityTransformer

from .models.copper import Person, Company, Opportunity, Activity
from .models.mcp import MCPPerson, MCPCompany, MCPOpportunity, MCPActivity

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Type aliases for better readability
MCPEntity = TypeVar('MCPEntity', MCPPerson, MCPCompany, MCPOpportunity, MCPActivity)
SearchResult = Dict[str, Any]

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
person_transformer = PersonTransformer(copper_model=Person, mcp_model=MCPPerson)
company_transformer = CompanyTransformer(copper_model=Company, mcp_model=MCPCompany)
opportunity_transformer = OpportunityTransformer(copper_model=Opportunity, mcp_model=MCPOpportunity)
activity_transformer = ActivityTransformer(copper_model=Activity, mcp_model=MCPActivity)

async def get_copper_client() -> CopperClient:
    """Get a configured Copper client.
    
    This dependency function creates and returns an authenticated CopperClient instance.
    It handles token retrieval and authentication errors.
    
    Returns:
        CopperClient: A configured client instance ready for API calls
        
    Raises:
        HTTPException: If authentication fails or token cannot be retrieved
    """
    try:
        token = get_auth_token()
        return CopperClient(token)
    except AuthenticationError as e:
        logger.error(f"Authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint.
    
    Returns:
        Dict[str, str]: Health status information including service name and version
    """
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
) -> List[SearchResult]:
    """Search across Copper entities.
    
    This endpoint performs a search across multiple entity types in Copper CRM.
    It can optionally filter by entity type and transforms results to MCP format.
    
    Args:
        query: Search query string to match against entities
        entity_type: Optional entity type to filter by (person, company, opportunity, activity)
        client: Copper client from dependency injection
        
    Returns:
        List[SearchResult]: List of search results in MCP format
        
    Raises:
        HTTPException: If search fails, returns invalid data, or encounters API errors
    """
    results: List[SearchResult] = []
    search_query = {"query": query}
    
    # Create entity clients
    people_client = PeopleClient(client)
    companies_client = CompaniesClient(client)
    opportunities_client = OpportunitiesClient(client)
    activities_client = ActivitiesClient(client)
    
    try:
        # Search people
        if not entity_type or entity_type == "person":
            try:
                people = await people_client.search(search_query)
                logger.info(f"Found {len(people)} people matching query: {query}")
                results.extend([
                    person_transformer.to_mcp(person)
                    for person in people
                ])
            except Exception as e:
                logger.error(f"Error searching people: {str(e)}")
            
        # Search companies
        if not entity_type or entity_type == "company":
            try:
                companies = await companies_client.search(search_query)
                logger.info(f"Found {len(companies)} companies matching query: {query}")
                results.extend([
                    company_transformer.to_mcp(company)
                    for company in companies
                ])
            except Exception as e:
                logger.error(f"Error searching companies: {str(e)}")
            
        # Search opportunities
        if not entity_type or entity_type == "opportunity":
            try:
                opportunities = await opportunities_client.search(search_query)
                logger.info(f"Found {len(opportunities)} opportunities matching query: {query}")
                results.extend([
                    opportunity_transformer.to_mcp(opp)
                    for opp in opportunities
                ])
            except Exception as e:
                logger.error(f"Error searching opportunities: {str(e)}")
            
        # Search activities
        if not entity_type or entity_type == "activity":
            try:
                activities = await activities_client.search(search_query)
                logger.info(f"Found {len(activities)} activities matching query: {query}")
                results.extend([
                    activity_transformer.to_mcp(activity)
                    for activity in activities
                ])
            except Exception as e:
                logger.error(f"Error searching activities: {str(e)}")
            
        return results
        
    except CopperAPIError as e:
        logger.error(f"Error from Copper API: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error from Copper API: {str(e)}"
        )
    except ValueError as e:
        logger.error(f"Invalid data received: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid data received: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )

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
        
    Raises:
        HTTPException: If person is not found or data is invalid
    """
    try:
        people_client = PeopleClient(client)
        person = await people_client.get(person_id)
        return person_transformer.to_mcp(person)
    except CopperAPIError as e:
        if "404" in str(e):
            logger.error(f"Person {person_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Person {person_id} not found"
            )
        logger.error(f"Error from Copper API: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error from Copper API: {str(e)}"
        )
    except ValueError as e:
        logger.error(f"Invalid data received: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid data received: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )

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
        
    Raises:
        HTTPException: If company is not found or data is invalid
    """
    try:
        companies_client = CompaniesClient(client)
        company = await companies_client.get(company_id)
        return company_transformer.to_mcp(company)
    except CopperAPIError as e:
        if "404" in str(e):
            logger.error(f"Company {company_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company {company_id} not found"
            )
        logger.error(f"Error from Copper API: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error from Copper API: {str(e)}"
        )
    except ValueError as e:
        logger.error(f"Invalid data received: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid data received: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )

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
        
    Raises:
        HTTPException: If opportunity is not found or data is invalid
    """
    try:
        opportunities_client = OpportunitiesClient(client)
        opportunity = await opportunities_client.get(opportunity_id)
        return opportunity_transformer.to_mcp(opportunity)
    except CopperAPIError as e:
        if "404" in str(e):
            logger.error(f"Opportunity {opportunity_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Opportunity {opportunity_id} not found"
            )
        logger.error(f"Error from Copper API: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error from Copper API: {str(e)}"
        )
    except ValueError as e:
        logger.error(f"Invalid data received: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid data received: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )

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
        
    Raises:
        HTTPException: If activity is not found or data is invalid
    """
    try:
        activities_client = ActivitiesClient(client)
        activity = await activities_client.get(activity_id)
        return activity_transformer.to_mcp(activity)
    except CopperAPIError as e:
        if "404" in str(e):
            logger.error(f"Activity {activity_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Activity {activity_id} not found"
            )
        logger.error(f"Error from Copper API: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error from Copper API: {str(e)}"
        )
    except ValueError as e:
        logger.error(f"Invalid data received: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid data received: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        ) 