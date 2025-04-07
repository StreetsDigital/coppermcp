"""Base client for interacting with the Copper CRM API.

This module provides the foundation for making authenticated requests to the Copper API.
"""
from typing import Any, Dict, Optional
import requests
from fastapi import HTTPException

from ..config import settings


class CopperAPIError(Exception):
    """Custom exception for Copper API errors."""
    
    def __init__(self, status_code: int, message: str, response: Optional[Dict[str, Any]] = None):
        """Initialize the error with status code and message.
        
        Args:
            status_code: HTTP status code from the API
            message: Error message
            response: Optional raw response data
        """
        self.status_code = status_code
        self.message = message
        self.response = response
        super().__init__(self.message)


class CopperBaseClient:
    """Base client for making authenticated requests to the Copper API."""
    
    def __init__(self):
        """Initialize the client with configuration from settings."""
        self.base_url = settings.copper_api_base_url
        self.session = requests.Session()
        self._setup_auth_headers()
    
    def _setup_auth_headers(self) -> None:
        """Configure authentication headers for all requests."""
        self.session.headers.update({
            'X-PW-AccessToken': settings.copper_api_key,
            'X-PW-Application': 'developer_api',
            'X-PW-UserEmail': settings.copper_user_email,
            'Content-Type': 'application/json'
        })
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and raise appropriate exceptions.
        
        Args:
            response: Response from the Copper API
            
        Returns:
            Dict containing the response data
            
        Raises:
            HTTPException: For client/server errors with appropriate status codes
        """
        try:
            response_data = response.json() if response.content else {}
        except ValueError:
            response_data = {}
        
        if response.status_code == 429:
            # Rate limit exceeded
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        
        if response.status_code >= 500:
            # Server error
            raise HTTPException(
                status_code=502,
                detail="Copper API server error"
            )
        
        if response.status_code in (401, 403):
            # Authentication/authorization error
            raise HTTPException(
                status_code=response.status_code,
                detail="Authentication failed with Copper API"
            )
        
        if response.status_code == 404:
            # Not found
            raise HTTPException(
                status_code=404,
                detail="Resource not found in Copper API"
            )
        
        if response.status_code >= 400:
            # Other client errors
            error_message = response_data.get('message', 'Unknown error occurred')
            raise HTTPException(
                status_code=response.status_code,
                detail=error_message
            )
        
        return response_data
    
    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request to the Copper API.
        
        Args:
            endpoint: API endpoint path
            params: Optional query parameters
            
        Returns:
            Dict containing the response data
        """
        response = self.session.get(
            f"{self.base_url}/{endpoint.lstrip('/')}",
            params=params
        )
        return self._handle_response(response)
    
    def _post(self, endpoint: str, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a POST request to the Copper API.
        
        Args:
            endpoint: API endpoint path
            json: Optional request body
            
        Returns:
            Dict containing the response data
        """
        response = self.session.post(
            f"{self.base_url}/{endpoint.lstrip('/')}",
            json=json
        )
        return self._handle_response(response)
    
    def _put(self, endpoint: str, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a PUT request to the Copper API.
        
        Args:
            endpoint: API endpoint path
            json: Optional request body
            
        Returns:
            Dict containing the response data
        """
        response = self.session.put(
            f"{self.base_url}/{endpoint.lstrip('/')}",
            json=json
        )
        return self._handle_response(response)
    
    def _delete(self, endpoint: str) -> Dict[str, Any]:
        """Make a DELETE request to the Copper API.
        
        Args:
            endpoint: API endpoint path
            
        Returns:
            Dict containing the response data
        """
        response = self.session.delete(
            f"{self.base_url}/{endpoint.lstrip('/')}"
        )
        return self._handle_response(response) 