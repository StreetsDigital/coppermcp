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

from typing import Dict, Any, List, Optional
from .base import CopperClient

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
        page_size: Optional[int] = None,
        page_number: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """List people.
        
        Args:
            page_size: Number of records to return per page
            page_number: Page number to return
            
        Returns:
            List[Dict[str, Any]]: List of people
        """
        params = {}
        if page_size is not None:
            params["page_size"] = page_size
        if page_number is not None:
            params["page_number"] = page_number
            
        return await self.client.get("/people", params=params)
    
    async def get(self, person_id: int) -> Dict[str, Any]:
        """Get a person by ID.
        
        Args:
            person_id: ID of the person
            
        Returns:
            Dict[str, Any]: Person details
        """
        return await self.client.get(f"/people/{person_id}")
    
    async def create(self, person: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new person.
        
        Args:
            person: Person data
            
        Returns:
            Dict[str, Any]: Created person
        """
        return await self.client.post("/people", json=person)
    
    async def update(self, person_id: int, person: Dict[str, Any]) -> Dict[str, Any]:
        """Update a person.
        
        Args:
            person_id: ID of the person to update
            person: Updated person data
            
        Returns:
            Dict[str, Any]: Updated person
        """
        return await self.client.put(f"/people/{person_id}", json=person)
    
    async def delete(self, person_id: int) -> None:
        """Delete a person.
        
        Args:
            person_id: ID of the person to delete
        """
        await self.client.delete(f"/people/{person_id}")
    
    async def search(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for people.
        
        Args:
            query: Search criteria
            
        Returns:
            List[Dict[str, Any]]: Matching people
        """
        return await self.client.post("/people/search", json=query) 