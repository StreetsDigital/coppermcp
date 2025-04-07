"""Companies client for Copper CRM API.

This module provides the client class for interacting with companies in Copper CRM.

AI Usage Guide:
--------------
Common company-related requests and how to handle them:

1. Search/Find Companies:
   "Find ACME Corporation's details"
   ```python
   companies = await client.companies.search({"name": "ACME"})
   if companies:
       company = companies[0]
       print(f"Name: {company.name}")
       print(f"Industry: {company.industry}")
       print(f"Website: {company.website}")
   ```

   "Show me all companies in the technology industry"
   ```python
   tech_companies = await client.companies.search({"industry": "Technology"})
   ```

2. Create Companies:
   "Add Globex Corporation as a new company"
   ```python
   company = await client.companies.create(CompanyCreate(
       name="Globex Corporation",
       industry="Technology",
       website="https://globex.com"
   ))
   ```

   "Create company record for Initech with their details"
   ```python
   company = await client.companies.create(CompanyCreate(
       name="Initech",
       industry="Software",
       website="https://initech.com",
       address={"street": "123 Tech Lane", "city": "Austin", "state": "TX"}
   ))
   ```

3. Update Companies:
   "Update ACME's website to www.acme-new.com"
   ```python
   # First find ACME
   companies = await client.companies.search({"name": "ACME"})
   if companies:
       await client.companies.update(
           companies[0].id,
           CompanyUpdate(website="https://www.acme-new.com")
       )
   ```

   "Change Initech's industry to Consulting"
   ```python
   await client.companies.update(
       company_id,
       CompanyUpdate(industry="Consulting")
   )
   ```

4. Delete Companies:
   "Remove Globex Corporation's record"
   ```python
   # Warning: This will affect all related records
   await client.companies.delete(company_id)
   ```

Common Patterns:
- Search by name before creating to avoid duplicates
- Handle related records (people, opportunities) appropriately
- Maintain consistent industry categorization
- Consider impact on related records when deleting
- Use full URLs for websites (add https:// if missing)
"""

from typing import Dict, Any, List, Optional
from .base import CopperClient
from ..models.companies import Company, CompanyCreate, CompanyUpdate


class CompaniesClient:
    """Client for managing companies in Copper CRM."""
    
    def __init__(self, client: CopperClient):
        """Initialize the companies client.
        
        Args:
            client: The base Copper client
        """
        self.client = client
    
    async def list(
        self,
        page_size: Optional[int] = None,
        page_number: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """List companies.
        
        Args:
            page_size: Number of records to return per page
            page_number: Page number to return
            
        Returns:
            List[Dict[str, Any]]: List of companies
        """
        params = {}
        if page_size is not None:
            params["page_size"] = page_size
        if page_number is not None:
            params["page_number"] = page_number
            
        return await self.client.get("/companies", params=params)
    
    async def get(self, company_id: int) -> Dict[str, Any]:
        """Get a company by ID.
        
        Args:
            company_id: ID of the company
            
        Returns:
            Dict[str, Any]: Company details
        """
        return await self.client.get(f"/companies/{company_id}")
    
    async def create(self, company: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new company.
        
        Args:
            company: Company data
            
        Returns:
            Dict[str, Any]: Created company
        """
        return await self.client.post("/companies", json=company)
    
    async def update(self, company_id: int, company: Dict[str, Any]) -> Dict[str, Any]:
        """Update a company.
        
        Args:
            company_id: ID of the company to update
            company: Updated company data
            
        Returns:
            Dict[str, Any]: Updated company
        """
        return await self.client.put(f"/companies/{company_id}", json=company)
    
    async def delete(self, company_id: int) -> None:
        """Delete a company.
        
        Args:
            company_id: ID of the company to delete
        """
        await self.client.delete(f"/companies/{company_id}")
    
    async def search(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for companies.
        
        Args:
            query: Search criteria
            
        Returns:
            List[Dict[str, Any]]: Matching companies
        """
        return await self.client.post("/companies/search", json=query) 