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

from typing import Dict, Any, List, Optional, AsyncIterator, Union
from pydantic import BaseModel, Field, field_validator, ConfigDict, AnyHttpUrl
from .base import CopperClient
from ..models.companies import Company, CompanyCreate, CompanyUpdate


class PaginationParams(BaseModel):
    """Parameters for paginated requests."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    page_number: Optional[int] = Field(1, ge=1)
    page_size: Optional[int] = Field(20, ge=1, le=200)

    @field_validator('page_size')
    @classmethod
    def validate_page_size(cls, v: int) -> int:
        """Validate page size is within API limits."""
        if v > 200:
            raise ValueError("page_size cannot exceed 200")
        return v

class SearchQuery(BaseModel):
    """Search query parameters."""
    query: Optional[str] = None
    name: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[AnyHttpUrl] = None
    assignee_id: Optional[int] = Field(None, gt=0)
    tags: Optional[List[str]] = None
    custom_fields: Optional[List[Dict[str, Any]]] = None

    @field_validator('website', mode='before')
    @classmethod
    def validate_website(cls, v: Optional[str]) -> Optional[str]:
        """Ensure website URLs have a protocol."""
        if v and not v.startswith(('http://', 'https://')):
            return f'https://{v}'
        return v

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
        pagination: Optional[PaginationParams] = None
    ) -> List[Dict[str, Any]]:
        """List companies.
        
        Args:
            pagination: Optional pagination parameters
            
        Returns:
            List[Dict[str, Any]]: List of companies
        """
        params = pagination.dict(exclude_none=True) if pagination else {}
        return await self.client.get("/companies", params=params)
    
    async def list_all(self) -> AsyncIterator[Dict[str, Any]]:
        """List all companies using automatic pagination.
        
        Yields:
            Dict[str, Any]: Each company record
        """
        page_number = 1
        while True:
            pagination = PaginationParams(page_size=200, page_number=page_number)
            results = await self.list(pagination)
            
            if not results:
                break
                
            for result in results:
                yield result
                
            page_number += 1
    
    async def get(self, company_id: int) -> Dict[str, Any]:
        """Get a company by ID.
        
        Args:
            company_id: ID of the company
            
        Returns:
            Dict[str, Any]: Company details
            
        Raises:
            ValueError: If company_id is not positive
        """
        if company_id <= 0:
            raise ValueError("company_id must be positive")
            
        return await self.client.get(f"/companies/{company_id}")
    
    async def create(self, company: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new company.
        
        Args:
            company: Company data
            
        Returns:
            Dict[str, Any]: Created company
            
        Raises:
            ValueError: If required fields are missing
        """
        if not company.get("name"):
            raise ValueError("name is required")
            
        # Ensure website has protocol
        if website := company.get("website"):
            if isinstance(website, str) and not website.startswith(('http://', 'https://')):
                company["website"] = f'https://{website}'
            
        return await self.client.post("/companies", json=company)
    
    async def update(self, company_id: int, company: Dict[str, Any]) -> Dict[str, Any]:
        """Update a company.
        
        Args:
            company_id: ID of the company to update
            company: Updated company data
            
        Returns:
            Dict[str, Any]: Updated company
            
        Raises:
            ValueError: If company_id is not positive
        """
        if company_id <= 0:
            raise ValueError("company_id must be positive")
            
        # Ensure website has protocol
        if website := company.get("website"):
            if isinstance(website, str) and not website.startswith(('http://', 'https://')):
                company["website"] = f'https://{website}'
            
        return await self.client.put(f"/companies/{company_id}", json=company)
    
    async def delete(self, company_id: int) -> None:
        """Delete a company.
        
        Args:
            company_id: ID of the company to delete
            
        Raises:
            ValueError: If company_id is not positive
        """
        if company_id <= 0:
            raise ValueError("company_id must be positive")
            
        await self.client.delete(f"/companies/{company_id}")
    
    async def search(self, query: Union[Dict[str, Any], SearchQuery]) -> List[Dict[str, Any]]:
        """Search for companies.
        
        Args:
            query: Search criteria, either as a dict or SearchQuery model
            
        Returns:
            List[Dict[str, Any]]: Matching companies
            
        Raises:
            ValueError: If query validation fails
        """
        if isinstance(query, dict):
            query = SearchQuery(**query)
            
        return await self.client.post("/companies/search", json=query.dict(exclude_none=True))
    
    async def bulk_create(self, companies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create multiple companies in one request.
        
        Args:
            companies: List of company data
            
        Returns:
            List[Dict[str, Any]]: List of created companies
            
        Raises:
            ValueError: If any required fields are missing
        """
        if not companies:
            raise ValueError("companies list cannot be empty")
            
        for company in companies:
            if not company.get("name"):
                raise ValueError("name is required for all companies")
                
            # Ensure website has protocol
            if website := company.get("website"):
                if isinstance(website, str) and not website.startswith(('http://', 'https://')):
                    company["website"] = f'https://{website}'
                
        return await self.client.post("/companies/bulk", json={"companies": companies})
    
    async def bulk_update(
        self,
        updates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Update multiple companies in one request.
        
        Args:
            updates: List of company updates, each must include 'id'
            
        Returns:
            List[Dict[str, Any]]: List of updated companies
            
        Raises:
            ValueError: If any required fields are missing
        """
        if not updates:
            raise ValueError("updates list cannot be empty")
            
        for update in updates:
            if not update.get("id"):
                raise ValueError("id is required for all updates")
                
            # Ensure website has protocol
            if website := update.get("website"):
                if isinstance(website, str) and not website.startswith(('http://', 'https://')):
                    update["website"] = f'https://{website}'
                
        return await self.client.put("/companies/bulk", json={"companies": updates}) 