"""
Copper CRM MCP Server

This server implements the Model Context Protocol for Copper CRM integration.
It provides tools for managing contacts, companies, opportunities, tasks, and activities through
a standardized MCP interface.

Supported Features:
- Resources: Contact data, Company data, Task data, Opportunity data, Activity data
- Tools: Search, Create, Update, Delete operations
- Transport: STDIO and HTTP
"""

from typing import Dict, List, Any
from app.mcp.server import FastMCP
from app.copper.client import CopperClient
from app.models.copper import Person, Company, Opportunity, Activity, Task
from app.mapping.transform import transform_to_mcp, transform_from_copper

# Initialize FastMCP server
mcp = FastMCP("copper")

# Initialize Copper client
copper_client = CopperClient()

@mcp.tool()
async def search_people(query: str) -> List[Dict[str, Any]]:
    """Search for people in Copper CRM.
    
    Args:
        query: Search query string for finding people
        
    Returns:
        List of people matching the search query in MCP format
    """
    results = await copper_client.people.search(query)
    return [transform_to_mcp(result, "person") for result in results]

@mcp.tool()
async def get_person(person_id: str) -> Dict[str, Any]:
    """Get details of a specific person from Copper CRM.
    
    Args:
        person_id: The ID of the person to retrieve
        
    Returns:
        Person details in MCP format
    """
    person = await copper_client.people.get(person_id)
    return transform_to_mcp(person, "person")

@mcp.tool()
async def create_person(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new person in Copper CRM.
    
    Args:
        data: Person data in MCP format
        
    Returns:
        Created person details in MCP format
    """
    copper_data = transform_from_copper(data, Person)
    result = await copper_client.people.create(copper_data)
    return transform_to_mcp(result, "person")

@mcp.tool()
async def update_person(person_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Update an existing person in Copper CRM.
    
    Args:
        person_id: The ID of the person to update
        data: Updated person data in MCP format
        
    Returns:
        Updated person details in MCP format
    """
    copper_data = transform_from_copper(data, Person)
    result = await copper_client.people.update(person_id, copper_data)
    return transform_to_mcp(result, "person")

@mcp.tool()
async def delete_person(person_id: str) -> Dict[str, Any]:
    """Delete a person from Copper CRM.
    
    Args:
        person_id: The ID of the person to delete
        
    Returns:
        Success status
    """
    await copper_client.people.delete(person_id)
    return {"status": "success", "message": f"Person {person_id} deleted successfully"}

@mcp.tool()
async def search_companies(query: str) -> List[Dict[str, Any]]:
    """Search for companies in Copper CRM.
    
    Args:
        query: Search query string for finding companies
        
    Returns:
        List of companies matching the search query in MCP format
    """
    results = await copper_client.companies.search(query)
    return [transform_to_mcp(result, "company") for result in results]

@mcp.tool()
async def get_company(company_id: str) -> Dict[str, Any]:
    """Get details of a specific company from Copper CRM.
    
    Args:
        company_id: The ID of the company to retrieve
        
    Returns:
        Company details in MCP format
    """
    company = await copper_client.companies.get(company_id)
    return transform_to_mcp(company, "company")

@mcp.tool()
async def create_company(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new company in Copper CRM.
    
    Args:
        data: Company data in MCP format
        
    Returns:
        Created company details in MCP format
    """
    copper_data = transform_from_copper(data, Company)
    result = await copper_client.companies.create(copper_data)
    return transform_to_mcp(result, "company")

@mcp.tool()
async def update_company(company_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Update an existing company in Copper CRM.
    
    Args:
        company_id: The ID of the company to update
        data: Updated company data in MCP format
        
    Returns:
        Updated company details in MCP format
    """
    copper_data = transform_from_copper(data, Company)
    result = await copper_client.companies.update(company_id, copper_data)
    return transform_to_mcp(result, "company")

@mcp.tool()
async def delete_company(company_id: str) -> Dict[str, Any]:
    """Delete a company from Copper CRM.
    
    Args:
        company_id: The ID of the company to delete
        
    Returns:
        Success status
    """
    await copper_client.companies.delete(company_id)
    return {"status": "success", "message": f"Company {company_id} deleted successfully"}

@mcp.tool()
async def get_task(task_id: str) -> Dict[str, Any]:
    """Get details of a specific task from Copper CRM.
    
    Args:
        task_id: The ID of the task to retrieve
        
    Returns:
        Task details in MCP format
    """
    task = await copper_client.tasks.get(task_id)
    return transform_to_mcp(task, "task")

@mcp.tool()
async def create_task(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new task in Copper CRM.
    
    Args:
        data: Task data in MCP format
        
    Returns:
        Created task details in MCP format
    """
    copper_data = transform_from_copper(data, Task)
    result = await copper_client.tasks.create(copper_data)
    return transform_to_mcp(result, "task")

@mcp.tool()
async def update_task(task_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Update an existing task in Copper CRM.
    
    Args:
        task_id: The ID of the task to update
        data: Updated task data in MCP format
        
    Returns:
        Updated task details in MCP format
    """
    copper_data = transform_from_copper(data, Task)
    result = await copper_client.tasks.update(task_id, copper_data)
    return transform_to_mcp(result, "task")

@mcp.tool()
async def delete_task(task_id: str) -> Dict[str, Any]:
    """Delete a task from Copper CRM.
    
    Args:
        task_id: The ID of the task to delete
        
    Returns:
        Success status
    """
    await copper_client.tasks.delete(task_id)
    return {"status": "success", "message": f"Task {task_id} deleted successfully"}

@mcp.tool()
async def search_tasks(query: str) -> List[Dict[str, Any]]:
    """Search for tasks in Copper CRM.
    
    Args:
        query: Search query string for finding tasks
        
    Returns:
        List of tasks matching the search query in MCP format
    """
    results = await copper_client.tasks.search(query)
    return [transform_to_mcp(result, "task") for result in results]

@mcp.tool()
async def get_opportunity(opportunity_id: str) -> Dict[str, Any]:
    """Get details of a specific opportunity from Copper CRM.
    
    Args:
        opportunity_id: The ID of the opportunity to retrieve
        
    Returns:
        Opportunity details in MCP format
    """
    opportunity = await copper_client.opportunities.get(opportunity_id)
    return transform_to_mcp(opportunity, "opportunity")

@mcp.tool()
async def create_opportunity(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new opportunity in Copper CRM.
    
    Args:
        data: Opportunity data in MCP format
        
    Returns:
        Created opportunity details in MCP format
    """
    copper_data = transform_from_copper(data, Opportunity)
    result = await copper_client.opportunities.create(copper_data)
    return transform_to_mcp(result, "opportunity")

@mcp.tool()
async def update_opportunity(opportunity_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Update an existing opportunity in Copper CRM.
    
    Args:
        opportunity_id: The ID of the opportunity to update
        data: Updated opportunity data in MCP format
        
    Returns:
        Updated opportunity details in MCP format
    """
    copper_data = transform_from_copper(data, Opportunity)
    result = await copper_client.opportunities.update(opportunity_id, copper_data)
    return transform_to_mcp(result, "opportunity")

@mcp.tool()
async def delete_opportunity(opportunity_id: str) -> Dict[str, Any]:
    """Delete an opportunity from Copper CRM.
    
    Args:
        opportunity_id: The ID of the opportunity to delete
        
    Returns:
        Success status
    """
    await copper_client.opportunities.delete(opportunity_id)
    return {"status": "success", "message": f"Opportunity {opportunity_id} deleted successfully"}

@mcp.tool()
async def search_opportunities(query: str) -> List[Dict[str, Any]]:
    """Search for opportunities in Copper CRM.
    
    Args:
        query: Search query string for finding opportunities
        
    Returns:
        List of opportunities matching the search query in MCP format
    """
    results = await copper_client.opportunities.search(query)
    return [transform_to_mcp(result, "opportunity") for result in results]

@mcp.tool()
async def get_activity(activity_id: str) -> Dict[str, Any]:
    """Get details of a specific activity from Copper CRM.
    
    Args:
        activity_id: The ID of the activity to retrieve
        
    Returns:
        Activity details in MCP format
    """
    activity = await copper_client.activities.get(activity_id)
    return transform_to_mcp(activity, "activity")

@mcp.tool()
async def create_activity(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new activity in Copper CRM.
    
    Args:
        data: Activity data in MCP format
        
    Returns:
        Created activity details in MCP format
    """
    copper_data = transform_from_copper(data, Activity)
    result = await copper_client.activities.create(copper_data)
    return transform_to_mcp(result, "activity")

@mcp.tool()
async def update_activity(activity_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Update an existing activity in Copper CRM.
    
    Args:
        activity_id: The ID of the activity to update
        data: Updated activity data in MCP format
        
    Returns:
        Updated activity details in MCP format
    """
    copper_data = transform_from_copper(data, Activity)
    result = await copper_client.activities.update(activity_id, copper_data)
    return transform_to_mcp(result, "activity")

@mcp.tool()
async def delete_activity(activity_id: str) -> Dict[str, Any]:
    """Delete an activity from Copper CRM.
    
    Args:
        activity_id: The ID of the activity to delete
        
    Returns:
        Success status
    """
    await copper_client.activities.delete(activity_id)
    return {"status": "success", "message": f"Activity {activity_id} deleted successfully"}

@mcp.tool()
async def search_activities(query: str) -> List[Dict[str, Any]]:
    """Search for activities in Copper CRM.
    
    Args:
        query: Search query string for finding activities
        
    Returns:
        List of activities matching the search query in MCP format
    """
    results = await copper_client.activities.search(query)
    return [transform_to_mcp(result, "activity") for result in results]

@mcp.tool()
async def get_entity_activities(entity_id: str, entity_type: str) -> List[Dict[str, Any]]:
    """Get all activities associated with a specific entity in Copper CRM.
    
    Args:
        entity_id: The ID of the entity (person, company, opportunity, or task)
        entity_type: The type of entity ("person", "company", "opportunity", or "task")
        
    Returns:
        List of activities associated with the entity in MCP format
    """
    valid_types = ["person", "company", "opportunity", "task"]
    if entity_type not in valid_types:
        raise ValueError(f"Invalid entity_type. Must be one of: {', '.join(valid_types)}")
        
    results = await copper_client.activities.list_for_entity(entity_type, entity_id)
    return [transform_to_mcp(result, "activity") for result in results]

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio") 