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

from app.models.copper import Person, PersonCreate, PersonUpdate

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
        """Initialize the client.
        
        Args:
            client: The base Copper client
        """
        self.client = client
        self.endpoint = "people"
    
    async def list(self, page_size: int = 25, page_number: int = 1) -> List[Person]:
        """List people with pagination.
        
        Args:
            page_size: Number of records per page
            page_number: Page number to fetch
            
        Returns:
            List[Person]: List of people
        """
        params = {
            'page_size': page_size,
            'page': page_number
        }
        response = await self.client.get(self.endpoint, params=params)
        return [Person.model_validate(item) for item in response]
    
    async def get(self, person_id: int) -> Person:
        """Get a person by ID.
        
        Args:
            person_id: The ID of the person to get
            
        Returns:
            Person: The requested person
        """
        response = await self.client.get(f"{self.endpoint}/{person_id}")
        return Person.model_validate(response)
    
    async def create(self, person: PersonCreate) -> Person:
        """Create a new person.
        
        Args:
            person: The person data to create
            
        Returns:
            Person: The created person
        """
        response = await self.client.post(self.endpoint, json=person.model_dump(exclude_none=True))
        return Person.model_validate(response)
    
    async def update(self, person_id: int, person: PersonUpdate) -> Person:
        """Update a person.
        
        Args:
            person_id: The ID of the person to update
            person: The person data to update
            
        Returns:
            Person: The updated person
        """
        response = await self.client.put(
            f"{self.endpoint}/{person_id}",
            json=person.model_dump(exclude_none=True)
        )
        return Person.model_validate(response)
    
    async def delete(self, person_id: int) -> None:
        """Delete a person.
        
        Args:
            person_id: The ID of the person to delete
        """
        await self.client.delete(f"{self.endpoint}/{person_id}")
    
    async def search(self, query: Dict[str, Any]) -> List[Person]:
        """Search for people.
        
        Args:
            query: Search criteria
            
        Returns:
            List[Person]: List of matching people
        """
        response = await self.client.post(f"{self.endpoint}/search", json=query)
        return [Person.model_validate(item) for item in response]
    
    async def update_custom_fields(self, person_id: int, custom_fields: List[Dict[str, Any]]) -> Person:
        """Update custom fields for a person.
        
        Args:
            person_id: The ID of the person to update
            custom_fields: List of custom field updates
            
        Returns:
            Person: The updated person
        """
        response = await self.client.put(
            f"{self.endpoint}/{person_id}/custom_fields",
            json={"custom_fields": custom_fields}
        )
        return Person.model_validate(response)
    
    async def convert_lead(self, person_id: int, details: Dict[str, Any]) -> Person:
        """Convert a lead to a person.
        
        Args:
            person_id: The ID of the lead to convert
            details: Conversion details
            
        Returns:
            Person: The converted person
        """
        response = await self.client.post(f"{self.endpoint}/{person_id}/convert", json=details)
        return Person.model_validate(response)
    
    async def get_related(self, person_id: int, related_type: str) -> List[Dict[str, Any]]:
        """Get related entities for a person.
        
        Args:
            person_id: The ID of the person
            related_type: Type of related entities to get
            
        Returns:
            List[Dict[str, Any]]: List of related entities
        """
        return await self.client.get(f"{self.endpoint}/{person_id}/related/{related_type}")
    
    async def list_all(self) -> AsyncIterator[Dict[str, Any]]:
        """List all people using automatic pagination.
        
        Yields:
            Dict[str, Any]: Each person record
        """
        page_number = 1
        while True:
            pagination = PaginationParams(page_size=200, page_number=page_number)
            results = await self.list(pagination.page_size, pagination.page_number)
            
            if not results:
                break
                
            for result in results:
                yield result
                
            page_number += 1
    
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