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

from typing import Dict, Any, List, Optional
from datetime import datetime
from .base import CopperClient

from ..models.opportunities import Opportunity, OpportunityCreate, OpportunityUpdate


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
        page_size: Optional[int] = None,
        page_number: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """List opportunities.
        
        Args:
            page_size: Number of records to return per page
            page_number: Page number to return
            
        Returns:
            List[Dict[str, Any]]: List of opportunities
        """
        params = {}
        if page_size is not None:
            params["page_size"] = page_size
        if page_number is not None:
            params["page_number"] = page_number
            
        return await self.client.get("/opportunities", params=params)
    
    async def get(self, opportunity_id: int) -> Dict[str, Any]:
        """Get an opportunity by ID.
        
        Args:
            opportunity_id: ID of the opportunity
            
        Returns:
            Dict[str, Any]: Opportunity details
        """
        return await self.client.get(f"/opportunities/{opportunity_id}")
    
    async def create(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new opportunity.
        
        Args:
            opportunity: Opportunity data
            
        Returns:
            Dict[str, Any]: Created opportunity
        """
        return await self.client.post("/opportunities", json=opportunity)
    
    async def update(self, opportunity_id: int, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Update an opportunity.
        
        Args:
            opportunity_id: ID of the opportunity to update
            opportunity: Updated opportunity data
            
        Returns:
            Dict[str, Any]: Updated opportunity
        """
        return await self.client.put(f"/opportunities/{opportunity_id}", json=opportunity)
    
    async def delete(self, opportunity_id: int) -> None:
        """Delete an opportunity.
        
        Args:
            opportunity_id: ID of the opportunity to delete
        """
        await self.client.delete(f"/opportunities/{opportunity_id}")
    
    async def search(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for opportunities.
        
        Args:
            query: Search criteria
            
        Returns:
            List[Dict[str, Any]]: Matching opportunities
        """
        return await self.client.post("/opportunities/search", json=query) 