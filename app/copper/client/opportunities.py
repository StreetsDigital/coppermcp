"""Opportunities client for Copper CRM API.

This module provides the client class for interacting with opportunities in Copper CRM.

AI Usage Guide:
--------------
Common opportunity-related requests and how to handle them:

1. Search/List Opportunities:
   "Show me all open opportunities"
   ```python
   opportunities = await client.opportunities.search({"status": "Open"})
   ```

   "Find opportunities with ACME Corp"
   ```python
   # First find the company
   companies = await client.companies.search({"name": "ACME Corp"})
   if companies:
       opps = await client.opportunities.search({"company_id": companies[0].id})
   ```

   "List opportunities worth over $50,000"
   ```python
   high_value_opps = await client.opportunities.search({"min_value": 50000})
   ```

2. Create Opportunities:
   "Create new opportunity with ACME Corp for $100,000"
   ```python
   # First find or create the company
   companies = await client.companies.search({"name": "ACME Corp"})
   company_id = companies[0].id if companies else None
   
   if not company_id:
       company = await client.companies.create(CompanyCreate(name="ACME Corp"))
       company_id = company.id
   
   opp = await client.opportunities.create(OpportunityCreate(
       name="ACME Corp - Enterprise Deal",
       company_id=company_id,
       monetary_value=100000,
       pipeline_id=1,  # Assuming default sales pipeline
       pipeline_stage_id=1  # Assuming first stage
   ))
   ```

   "Add opportunity for software license renewal with Initech"
   ```python
   opp = await client.opportunities.create(OpportunityCreate(
       name="Initech - License Renewal 2024",
       company_id=company_id,
       monetary_value=25000,
       pipeline_id=1,
       pipeline_stage_id=1,
       close_date=datetime.now() + timedelta(days=30)
   ))
   ```

3. Update Opportunities:
   "Move ACME opportunity to Negotiation stage"
   ```python
   # First find the opportunity
   opps = await client.opportunities.search({"name": "ACME Corp"})
   if opps:
       await client.opportunities.update(
           opps[0].id,
           OpportunityUpdate(pipeline_stage_id=3)  # Assuming stage 3 is Negotiation
       )
   ```

   "Update deal value to $150,000"
   ```python
   await client.opportunities.update(
       opportunity_id,
       OpportunityUpdate(monetary_value=150000)
   )
   ```

4. Delete Opportunities:
   "Remove the Initech opportunity"
   ```python
   await client.opportunities.delete(opportunity_id)
   ```

Common Patterns:
- Always associate opportunities with companies
- Set realistic close dates
- Use consistent pipeline stages
- Track monetary values accurately
- Consider win probability when updating stages
- Keep opportunity names descriptive and consistent
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from .base import CopperClient, CopperAPIError

from ..models.opportunities import Opportunity, OpportunityCreate, OpportunityUpdate


class PaginationParams(BaseModel):
    """Parameters for paginating results."""
    
    page_size: Optional[int] = Field(None, le=200, gt=0)
    page_number: Optional[int] = Field(None, gt=0)


class OpportunitySearchQuery(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: Optional[str] = None
    company_id: Optional[int] = Field(None, gt=0)
    pipeline_id: Optional[int] = Field(None, gt=0)
    pipeline_stage_id: Optional[int] = Field(None, gt=0)
    status: Optional[str] = Field(None, pattern="^(Open|Won|Lost|Abandoned)$")
    min_value: Optional[float] = Field(None, gt=0)
    max_value: Optional[float] = Field(None, gt=0)
    close_date_start: Optional[datetime] = None
    close_date_end: Optional[datetime] = None
    assignee_id: Optional[int] = Field(None, gt=0)
    tags: Optional[List[str]] = None
    
    @field_validator("max_value")
    @classmethod
    def validate_max_value(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError("max_value must be non-negative")
        return v

    @field_validator("close_date_end")
    @classmethod
    def validate_close_date_end(cls, v: Optional[datetime], values: Dict[str, Any]) -> Optional[datetime]:
        close_date_start = values.get("close_date_start")
        if close_date_start and v and v < close_date_start:
            raise ValueError("close_date_end must be after close_date_start")
        return v

    @field_validator("company_id", "pipeline_id", "pipeline_stage_id", "assignee_id")
    @classmethod
    def validate_ids(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError("ID fields must be non-negative")
        return v


class OpportunitiesClient:
    """Client for managing opportunities in Copper CRM."""
    
    def __init__(self, client: CopperClient):
        """Initialize the opportunities client.
        
        Args:
            client: The base Copper client
        """
        self.client = client
    
    async def list(
        self,
        pagination: Optional[PaginationParams] = None
    ) -> List[Dict[str, Any]]:
        """List opportunities with pagination.
        
        Args:
            pagination: Optional pagination parameters
            
        Returns:
            List[Dict[str, Any]]: List of opportunities
        """
        params = pagination.dict(exclude_none=True) if pagination else {}
        return await self.client.get("/opportunities", params=params)
    
    async def list_all(self) -> List[Dict[str, Any]]:
        """List all opportunities by automatically handling pagination.
        
        Returns:
            List[Dict[str, Any]]: Complete list of opportunities
        """
        results = []
        page = 1
        while True:
            batch = await self.list(PaginationParams(page_number=page, page_size=200))
            if not batch:
                break
            results.extend(batch)
            page += 1
        return results
    
    async def get(self, opportunity_id: int) -> Dict[str, Any]:
        """Get an opportunity by ID.
        
        Args:
            opportunity_id: ID of the opportunity
            
        Returns:
            Dict[str, Any]: Opportunity details
            
        Raises:
            ValueError: If opportunity_id is not positive
            CopperAPIError: If opportunity is not found
        """
        if opportunity_id <= 0:
            raise ValueError("opportunity_id must be positive")
            
        return await self.client.get(f"/opportunities/{opportunity_id}")
    
    async def create(self, opportunity: Union[Dict[str, Any], OpportunityCreate]) -> Dict[str, Any]:
        """Create a new opportunity.
        
        Args:
            opportunity: Opportunity data or OpportunityCreate model
            
        Returns:
            Dict[str, Any]: Created opportunity
            
        Raises:
            ValueError: If required fields are missing
        """
        if isinstance(opportunity, OpportunityCreate):
            data = opportunity.dict(exclude_none=True)
        else:
            data = opportunity
            
        if not data.get("name"):
            raise ValueError("name is required")
        if not data.get("pipeline_id"):
            raise ValueError("pipeline_id is required")
        if not data.get("pipeline_stage_id"):
            raise ValueError("pipeline_stage_id is required")
            
        return await self.client.post("/opportunities", json=data)
    
    async def bulk_create(self, opportunities: List[Union[Dict[str, Any], OpportunityCreate]]) -> List[Dict[str, Any]]:
        """Create multiple opportunities in bulk.
        
        Args:
            opportunities: List of opportunity data or OpportunityCreate models
            
        Returns:
            List[Dict[str, Any]]: List of created opportunities
            
        Raises:
            ValueError: If opportunities list is empty or required fields are missing
        """
        if not opportunities:
            raise ValueError("opportunities list cannot be empty")
            
        results = []
        errors = []
        
        for i, opp in enumerate(opportunities):
            try:
                result = await self.create(opp)
                results.append(result)
            except ValueError as e:
                errors.append(f"Error in opportunity {i}: {str(e)}")
            except CopperAPIError as e:
                errors.append(f"API error in opportunity {i}: {str(e)}")
                
        if errors:
            raise ValueError(f"Bulk create failed with errors: {'; '.join(errors)}")
            
        return results
    
    async def update(
        self,
        opportunity_id: int,
        opportunity: Union[Dict[str, Any], OpportunityUpdate]
    ) -> Dict[str, Any]:
        """Update an opportunity.
        
        Args:
            opportunity_id: ID of the opportunity to update
            opportunity: Updated opportunity data or OpportunityUpdate model
            
        Returns:
            Dict[str, Any]: Updated opportunity
        """
        if isinstance(opportunity, OpportunityUpdate):
            data = opportunity.dict(exclude_none=True)
        else:
            data = opportunity
        return await self.client.put(f"/opportunities/{opportunity_id}", json=data)
    
    async def bulk_update(
        self,
        updates: List[tuple[int, Union[Dict[str, Any], OpportunityUpdate]]]
    ) -> List[Dict[str, Any]]:
        """Update multiple opportunities in bulk.
        
        Args:
            updates: List of tuples containing (opportunity_id, update_data)
            
        Returns:
            List[Dict[str, Any]]: List of updated opportunities
            
        Raises:
            ValueError: If updates list is empty or contains invalid data
            CopperAPIError: If any update operation fails
        """
        if not updates:
            raise ValueError("updates list cannot be empty")
            
        results = []
        errors = []
        
        for i, (opp_id, update_data) in enumerate(updates):
            try:
                result = await self.update(opp_id, update_data)
                results.append(result)
            except ValueError as e:
                errors.append(f"Error in update {i}: {str(e)}")
            except CopperAPIError as e:
                errors.append(f"API error in update {i}: {str(e)}")
                
        if errors:
            raise ValueError(f"Bulk update failed with errors: {'; '.join(errors)}")
            
        return results
    
    async def delete(self, opportunity_id: int) -> None:
        """Delete an opportunity.
        
        Args:
            opportunity_id: ID of the opportunity to delete
            
        Raises:
            CopperAPIError: If opportunity is not found
        """
        await self.client.delete(f"/opportunities/{opportunity_id}")
    
    async def search(
        self,
        query: Union[Dict[str, Any], OpportunitySearchQuery]
    ) -> List[Dict[str, Any]]:
        """Search for opportunities.
        
        Args:
            query: Search criteria as dict or OpportunitySearchQuery model
            
        Returns:
            List[Dict[str, Any]]: Matching opportunities
        """
        if isinstance(query, OpportunitySearchQuery):
            data = query.dict(exclude_none=True)
        else:
            data = query
        return await self.client.post("/opportunities/search", json=data) 