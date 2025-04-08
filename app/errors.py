"""
MCP-specific error handling for Copper CRM integration.

This module defines custom error types that conform to the MCP error handling
specifications while providing Copper-specific context and details.
"""

from typing import Optional, Any, Dict
from app.mcp.errors import MCPError, MCPValidationError

class CopperMCPError(MCPError):
    """Base error class for Copper MCP operations.
    
    Attributes:
        message: Error message
        code: Error code
        details: Additional error details
    """
    
    def __init__(
        self, 
        message: str, 
        code: Optional[str] = None, 
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.code = code or "COPPER_ERROR"
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to MCP-compatible dictionary format."""
        return {
            "error": {
                "type": self.code,
                "message": str(self),
                "details": self.details
            }
        }

class CopperValidationError(MCPValidationError):
    """Validation error for Copper data.
    
    Raised when data validation fails during transformation or processing.
    """
    
    def __init__(
        self, 
        message: str, 
        field: Optional[str] = None, 
        value: Optional[Any] = None
    ):
        super().__init__(message)
        self.field = field
        self.value = value

    def to_dict(self) -> Dict[str, Any]:
        """Convert validation error to MCP-compatible dictionary format."""
        return {
            "error": {
                "type": "VALIDATION_ERROR",
                "message": str(self),
                "details": {
                    "field": self.field,
                    "value": self.value
                }
            }
        }

class CopperAuthenticationError(CopperMCPError):
    """Authentication error for Copper API operations."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            details={"requires": ["api_token", "email"]}
        )

class CopperNotFoundError(CopperMCPError):
    """Error raised when a requested resource is not found."""
    
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} with ID {resource_id} not found",
            code="NOT_FOUND_ERROR",
            details={
                "resource_type": resource_type,
                "resource_id": resource_id
            }
        )

class CopperRateLimitError(CopperMCPError):
    """Error raised when API rate limits are exceeded."""
    
    def __init__(self, retry_after: Optional[int] = None):
        super().__init__(
            message="API rate limit exceeded",
            code="RATE_LIMIT_ERROR",
            details={"retry_after": retry_after} if retry_after else {}
        ) 