"""
Copper CRM MCP Transport Layer

Implements the MCP transport protocol for Copper CRM operations.
Handles command processing and response formatting according to MCP specifications.
"""

from typing import Dict, Any, Optional, AsyncIterator
import json
import sys
import os
from app.mcp.transport import BaseTransport
from app.mcp.errors import MCPError, MCPValidationError
from app.copper.client import CopperClient
from app.models.copper import Person, Company, Opportunity, Activity, Task
from app.mapping.transform import transform_to_mcp, transform_from_copper

class CopperMCPTransport(BaseTransport):
    """MCP Transport implementation for Copper CRM."""

    def __init__(self, api_token: str, email: str):
        """Initialize the transport with Copper credentials.
        
        Args:
            api_token: Copper API token
            email: User email for authentication
        """
        super().__init__()
        self.client = CopperClient(api_token=api_token, email=email)
        self.command_handlers = {
            "search_people": self._handle_search_people,
            "get_person": self._handle_get_person,
            "create_person": self._handle_create_person,
            "search_companies": self._handle_search_companies,
            "get_company": self._handle_get_company,
            "get_task": self._handle_get_task,
            "create_task": self._handle_create_task,
            "update_task": self._handle_update_task,
            "delete_task": self._handle_delete_task,
            "search_tasks": self._handle_search_tasks,
            "get_opportunity": self._handle_get_opportunity,
            "create_opportunity": self._handle_create_opportunity,
            "update_opportunity": self._handle_update_opportunity,
            "delete_opportunity": self._handle_delete_opportunity,
            "search_opportunities": self._handle_search_opportunities,
            "get_activity": self._handle_get_activity,
            "create_activity": self._handle_create_activity,
            "update_activity": self._handle_update_activity,
            "delete_activity": self._handle_delete_activity,
            "search_activities": self._handle_search_activities,
            "get_entity_activities": self._handle_get_entity_activities,
        }

    async def run(self) -> None:
        """Run the transport loop.
        
        Continuously processes incoming commands and sends responses.
        """
        while True:
            try:
                command = await self.receive_command()
                response = await self.process_command(command)
                await self.send_response(response)
            except MCPError as e:
                await self.send_error(str(e))
            except Exception as e:
                await self.send_error(f"Unexpected error: {str(e)}")

    async def process_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Process an incoming MCP command.
        
        Args:
            command: The command to process
            
        Returns:
            The response to the command
            
        Raises:
            MCPError: If the command is invalid or processing fails
        """
        command_type = command.get("type")
        if not command_type:
            raise MCPError("Missing command type")

        handler = self.command_handlers.get(command_type)
        if not handler:
            raise MCPError(f"Unknown command type: {command_type}")

        try:
            return await handler(command.get("args", {}))
        except MCPValidationError as e:
            raise MCPError(f"Validation error: {str(e)}")
        except Exception as e:
            raise MCPError(f"Error processing command: {str(e)}")

    async def _handle_search_people(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle search_people command."""
        query = args.get("query")
        if not query:
            raise MCPValidationError("Missing query parameter")
        results = await self.client.people.search(query)
        return {
            "status": "success",
            "data": [transform_to_mcp(result, "person") for result in results]
        }

    async def _handle_get_person(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_person command."""
        person_id = args.get("person_id")
        if not person_id:
            raise MCPValidationError("Missing person_id parameter")
        person = await self.client.people.get(person_id)
        return {
            "status": "success",
            "data": transform_to_mcp(person, "person")
        }

    async def _handle_create_person(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle create_person command."""
        data = args.get("data")
        if not data:
            raise MCPValidationError("Missing data parameter")
        copper_data = transform_from_copper(data, Person)
        result = await self.client.people.create(copper_data)
        return {
            "status": "success",
            "data": transform_to_mcp(result, "person")
        }

    async def _handle_search_companies(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle search_companies command."""
        query = args.get("query")
        if not query:
            raise MCPValidationError("Missing query parameter")
        results = await self.client.companies.search(query)
        return {
            "status": "success",
            "data": [transform_to_mcp(result, "company") for result in results]
        }

    async def _handle_get_company(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_company command."""
        company_id = args.get("company_id")
        if not company_id:
            raise MCPValidationError("Missing company_id parameter")
        company = await self.client.companies.get(company_id)
        return {
            "status": "success",
            "data": transform_to_mcp(company, "company")
        }

    async def _handle_get_task(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_task command."""
        task_id = args.get("task_id")
        if not task_id:
            raise MCPValidationError("Missing task_id parameter")
        task = await self.client.tasks.get(task_id)
        return {
            "status": "success",
            "data": transform_to_mcp(task, "task")
        }

    async def _handle_create_task(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle create_task command."""
        data = args.get("data")
        if not data:
            raise MCPValidationError("Missing data parameter")
        copper_data = transform_from_copper(data, Task)
        result = await self.client.tasks.create(copper_data)
        return {
            "status": "success",
            "data": transform_to_mcp(result, "task")
        }

    async def _handle_update_task(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle update_task command."""
        task_id = args.get("task_id")
        data = args.get("data")
        if not task_id:
            raise MCPValidationError("Missing task_id parameter")
        if not data:
            raise MCPValidationError("Missing data parameter")
        copper_data = transform_from_copper(data, Task)
        result = await self.client.tasks.update(task_id, copper_data)
        return {
            "status": "success",
            "data": transform_to_mcp(result, "task")
        }

    async def _handle_delete_task(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle delete_task command."""
        task_id = args.get("task_id")
        if not task_id:
            raise MCPValidationError("Missing task_id parameter")
        await self.client.tasks.delete(task_id)
        return {
            "status": "success",
            "message": f"Task {task_id} deleted successfully"
        }

    async def _handle_search_tasks(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle search_tasks command."""
        query = args.get("query")
        if not query:
            raise MCPValidationError("Missing query parameter")
        results = await self.client.tasks.search(query)
        return {
            "status": "success",
            "data": [transform_to_mcp(result, "task") for result in results]
        }

    async def _handle_get_opportunity(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_opportunity command."""
        opportunity_id = args.get("opportunity_id")
        if not opportunity_id:
            raise MCPValidationError("Missing opportunity_id parameter")
        opportunity = await self.client.opportunities.get(opportunity_id)
        return {
            "status": "success",
            "data": transform_to_mcp(opportunity, "opportunity")
        }

    async def _handle_create_opportunity(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle create_opportunity command."""
        data = args.get("data")
        if not data:
            raise MCPValidationError("Missing data parameter")
        copper_data = transform_from_copper(data, Opportunity)
        result = await self.client.opportunities.create(copper_data)
        return {
            "status": "success",
            "data": transform_to_mcp(result, "opportunity")
        }

    async def _handle_update_opportunity(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle update_opportunity command."""
        opportunity_id = args.get("opportunity_id")
        data = args.get("data")
        if not opportunity_id:
            raise MCPValidationError("Missing opportunity_id parameter")
        if not data:
            raise MCPValidationError("Missing data parameter")
        copper_data = transform_from_copper(data, Opportunity)
        result = await self.client.opportunities.update(opportunity_id, copper_data)
        return {
            "status": "success",
            "data": transform_to_mcp(result, "opportunity")
        }

    async def _handle_delete_opportunity(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle delete_opportunity command."""
        opportunity_id = args.get("opportunity_id")
        if not opportunity_id:
            raise MCPValidationError("Missing opportunity_id parameter")
        await self.client.opportunities.delete(opportunity_id)
        return {
            "status": "success",
            "message": f"Opportunity {opportunity_id} deleted successfully"
        }

    async def _handle_search_opportunities(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle search_opportunities command."""
        query = args.get("query")
        if not query:
            raise MCPValidationError("Missing query parameter")
        results = await self.client.opportunities.search(query)
        return {
            "status": "success",
            "data": [transform_to_mcp(result, "opportunity") for result in results]
        }

    async def _handle_get_activity(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_activity command."""
        activity_id = args.get("activity_id")
        if not activity_id:
            raise MCPValidationError("Missing activity_id parameter")
        activity = await self.client.activities.get(activity_id)
        return {
            "status": "success",
            "data": transform_to_mcp(activity, "activity")
        }

    async def _handle_create_activity(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle create_activity command."""
        data = args.get("data")
        if not data:
            raise MCPValidationError("Missing data parameter")
        copper_data = transform_from_copper(data, Activity)
        result = await self.client.activities.create(copper_data)
        return {
            "status": "success",
            "data": transform_to_mcp(result, "activity")
        }

    async def _handle_update_activity(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle update_activity command."""
        activity_id = args.get("activity_id")
        data = args.get("data")
        if not activity_id:
            raise MCPValidationError("Missing activity_id parameter")
        if not data:
            raise MCPValidationError("Missing data parameter")
        copper_data = transform_from_copper(data, Activity)
        result = await self.client.activities.update(activity_id, copper_data)
        return {
            "status": "success",
            "data": transform_to_mcp(result, "activity")
        }

    async def _handle_delete_activity(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle delete_activity command."""
        activity_id = args.get("activity_id")
        if not activity_id:
            raise MCPValidationError("Missing activity_id parameter")
        await self.client.activities.delete(activity_id)
        return {
            "status": "success",
            "message": f"Activity {activity_id} deleted successfully"
        }

    async def _handle_search_activities(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle search_activities command."""
        query = args.get("query")
        if not query:
            raise MCPValidationError("Missing query parameter")
        results = await self.client.activities.search(query)
        return {
            "status": "success",
            "data": [transform_to_mcp(result, "activity") for result in results]
        }

    async def _handle_get_entity_activities(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_entity_activities command."""
        entity_id = args.get("entity_id")
        entity_type = args.get("entity_type")
        if not entity_id:
            raise MCPValidationError("Missing entity_id parameter")
        if not entity_type:
            raise MCPValidationError("Missing entity_type parameter")
        
        # Validate entity type
        valid_types = ["person", "company", "opportunity", "task"]
        if entity_type not in valid_types:
            raise MCPValidationError(f"Invalid entity_type. Must be one of: {', '.join(valid_types)}")
            
        results = await self.client.activities.list_for_entity(entity_type, entity_id)
        return {
            "status": "success",
            "data": [transform_to_mcp(result, "activity") for result in results]
        } 