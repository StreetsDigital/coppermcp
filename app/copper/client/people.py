"""People client for Copper CRM API.

This module provides the client class for interacting with people in Copper CRM.

AI Usage Guide:
--------------
Common people-related requests and how to handle them:

1. Search/Find People:
   "Find John Smith's contact info"
   ```python
   people = await client.people.search({"name": "John Smith"})
   if people:
       contact = people[0]
       print(f"Email: {contact.email}")
       print(f"Phone: {contact.phone}")
   ```

   "Show me all contacts at ACME Corp"
   ```python
   # First find the company
   companies = await client.companies.search({"name": "ACME Corp"})
   if companies:
       people = await client.people.search({"company_id": companies[0].id})
   ```

2. Create People:
   "Add Jane Doe (jane@example.com) as a new contact"
   ```python
   person = await client.people.create(PersonCreate(
       name="Jane Doe",
       emails=[{"email": "jane@example.com"}]
   ))
   ```

   "Create contact John Smith from ACME Corp"
   ```python
   # First find or create the company
   companies = await client.companies.search({"name": "ACME Corp"})
   company_id = companies[0].id if companies else None
   
   if not company_id:
       company = await client.companies.create(CompanyCreate(
           name="ACME Corp"
       ))
       company_id = company.id
   
   person = await client.people.create(PersonCreate(
       name="John Smith",
       company_id=company_id
   ))
   ```

3. Update People:
   "Update John's email to john.smith@newdomain.com"
   ```python
   # First find John
   people = await client.people.search({"name": "John Smith"})
   if people:
       await client.people.update(
           people[0].id,
           PersonUpdate(emails=[{"email": "john.smith@newdomain.com"}])
       )
   ```

   "Add a phone number for Jane"
   ```python
   await client.people.update(
       person_id,
       PersonUpdate(phone_numbers=[{"number": "+1-555-0123"}])
   )
   ```

4. Delete People:
   "Remove Jane's contact record"
   ```python
   await client.people.delete(person_id)
   ```

Common Patterns:
- Always search before creating to avoid duplicates
- Handle company associations appropriately
- Maintain all contact methods (email, phone, etc.)
- Consider related records (tasks, opportunities) when deleting
"""

from typing import Dict, Any, List, Optional, AsyncIterator, TypeVar, Union
from pydantic import BaseModel, Field, field_validator, ConfigDict
from .base import CopperClient

T = TypeVar('T')

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
    email: Optional[str] = None
    company_id: Optional[int] = Field(None, gt=0)
    assignee_id: Optional[int] = Field(None, gt=0)
    tags: Optional[List[str]] = None
    custom_fields: Optional[List[Dict[str, Any]]] = None

class PeopleClient:
    """Client for managing people in Copper CRM."""
    
    def __init__(self, client: CopperClient):
        """Initialize the people client.
        
        Args:
            client: The base Copper client
        """
        self.client = client
    
    async def list(
        self,
        pagination: Optional[PaginationParams] = None
    ) -> List[Dict[str, Any]]:
        """List people.
        
        Args:
            pagination: Optional pagination parameters
            
        Returns:
            List[Dict[str, Any]]: List of people
        """
        params = pagination.dict(exclude_none=True) if pagination else {}
        return await self.client.get("/people", params=params)
    
    async def list_all(self) -> AsyncIterator[Dict[str, Any]]:
        """List all people using automatic pagination.
        
        Yields:
            Dict[str, Any]: Each person record
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
    
    async def get(self, person_id: int) -> Dict[str, Any]:
        """Get a person by ID.
        
        Args:
            person_id: ID of the person
            
        Returns:
            Dict[str, Any]: Person details
            
        Raises:
            ValueError: If person_id is not positive
        """
        if person_id <= 0:
            raise ValueError("person_id must be positive")
            
        return await self.client.get(f"/people/{person_id}")
    
    async def create(self, person: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new person.
        
        Args:
            person: Person data
            
        Returns:
            Dict[str, Any]: Created person
            
        Raises:
            ValueError: If required fields are missing
        """
        if not person.get("name"):
            raise ValueError("name is required")
            
        return await self.client.post("/people", json=person)
    
    async def update(self, person_id: int, person: Dict[str, Any]) -> Dict[str, Any]:
        """Update a person.
        
        Args:
            person_id: ID of the person to update
            person: Updated person data
            
        Returns:
            Dict[str, Any]: Updated person
            
        Raises:
            ValueError: If person_id is not positive
        """
        if person_id <= 0:
            raise ValueError("person_id must be positive")
            
        return await self.client.put(f"/people/{person_id}", json=person)
    
    async def delete(self, person_id: int) -> None:
        """Delete a person.
        
        Args:
            person_id: ID of the person to delete
            
        Raises:
            ValueError: If person_id is not positive
        """
        if person_id <= 0:
            raise ValueError("person_id must be positive")
            
        await self.client.delete(f"/people/{person_id}")
    
    async def search(self, query: Union[Dict[str, Any], SearchQuery]) -> List[Dict[str, Any]]:
        """Search for people.
        
        Args:
            query: Search criteria, either as a dict or SearchQuery model
            
        Returns:
            List[Dict[str, Any]]: Matching people
            
        Raises:
            ValueError: If query validation fails
        """
        if isinstance(query, dict):
            query = SearchQuery(**query)
            
        return await self.client.post("/people/search", json=query.dict(exclude_none=True))
    
    async def bulk_create(self, people: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create multiple people in one request.
        
        Args:
            people: List of people data
            
        Returns:
            List[Dict[str, Any]]: List of created people
            
        Raises:
            ValueError: If any required fields are missing
        """
        if not people:
            raise ValueError("people list cannot be empty")
            
        for person in people:
            if not person.get("name"):
                raise ValueError("name is required for all people")
                
        return await self.client.post("/people/bulk", json={"people": people})
    
    async def bulk_update(
        self,
        updates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Update multiple people in one request.
        
        Args:
            updates: List of person updates, each must include 'id'
            
        Returns:
            List[Dict[str, Any]]: List of updated people
            
        Raises:
            ValueError: If any required fields are missing
        """
        if not updates:
            raise ValueError("updates list cannot be empty")
            
        for update in updates:
            if not update.get("id"):
                raise ValueError("id is required for all updates")
                
        return await self.client.put("/people/bulk", json={"people": updates}) 