"""MCP error types."""

from typing import Dict, Any, Optional

class MCPError(Exception):
    """Base error class for MCP operations."""
    
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.code = code or "MCP_ERROR"
        self.details = details or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format."""
        return {
            "error": {
                "type": self.code,
                "message": str(self),
                "details": self.details
            }
        }

class MCPValidationError(MCPError):
    """Error raised when validation fails."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, code="VALIDATION_ERROR", details=details) 