"""FastAPI-based MCP server implementation."""

from typing import Dict, Any, Callable, List, Optional, Union
from functools import wraps
import inspect
import asyncio
from ..transport import BaseTransport
from ..errors import MCPError, MCPValidationError

class FastMCP:
    """FastAPI-based MCP server."""
    
    def __init__(self, name: str):
        """Initialize the MCP server.
        
        Args:
            name: Name of the MCP server
        """
        self.name = name
        self.tools: Dict[str, Callable] = {}
        
    def tool(self, name: Optional[str] = None) -> Callable:
        """Decorator to register a tool.
        
        Args:
            name: Optional name for the tool. If not provided, uses function name.
            
        Returns:
            Decorator function
        """
        def decorator(func: Callable) -> Callable:
            tool_name = name or func.__name__
            
            @wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    if inspect.iscoroutinefunction(func):
                        result = await func(*args, **kwargs)
                    else:
                        result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    if isinstance(e, MCPError):
                        raise
                    raise MCPError(str(e))
                    
            self.tools[tool_name] = wrapper
            return wrapper
            
        return decorator
        
    async def process_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Process an MCP command.
        
        Args:
            command: The command to process
            
        Returns:
            The response from processing the command
            
        Raises:
            MCPError: If command processing fails
        """
        try:
            tool_name = command.get("tool")
            if not tool_name:
                raise MCPValidationError("Missing tool name")
                
            tool = self.tools.get(tool_name)
            if not tool:
                raise MCPValidationError(f"Unknown tool: {tool_name}")
                
            args = command.get("args", {})
            result = await tool(**args)
            
            return {
                "status": "success",
                "result": result
            }
            
        except Exception as e:
            if isinstance(e, MCPError):
                return e.to_dict()
            return MCPError(str(e)).to_dict()
            
    def run(self, transport: Union[str, BaseTransport] = "stdio") -> None:
        """Run the MCP server.
        
        Args:
            transport: Transport to use ("stdio" or BaseTransport instance)
        """
        if isinstance(transport, str):
            if transport == "stdio":
                from ..transport.stdio import STDIOTransport
                transport = STDIOTransport()
            else:
                raise ValueError(f"Unknown transport: {transport}")
                
        asyncio.run(transport.run()) 