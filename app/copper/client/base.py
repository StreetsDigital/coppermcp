"""Base client for Copper CRM API.

This module provides the base client class for interacting with the Copper CRM API.
It handles authentication, request building, and response parsing.
"""
import aiohttp
from typing import Dict, Any, Optional, List, Union
from urllib.parse import urljoin

class CopperClient:
    """Base client for Copper CRM API."""
    
    BASE_URL = "https://api.copper.com/developer_api/v1/"
    
    def __init__(self, auth_token: str):
        """Initialize the client.
        
        Args:
            auth_token: The authentication token for Copper API
        """
        self.auth_token = auth_token
        self.session = None
    
    async def _ensure_session(self) -> None:
        """Ensure an aiohttp session exists."""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={
                    "X-PW-AccessToken": self.auth_token,
                    "X-PW-Application": "developer_api",
                    "Content-Type": "application/json"
                }
            )
    
    async def close(self) -> None:
        """Close the client session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    def _build_url(self, endpoint: str) -> str:
        """Build a full URL for an API endpoint.
        
        Args:
            endpoint: The API endpoint path
            
        Returns:
            str: The complete URL
        """
        return urljoin(self.BASE_URL, endpoint.lstrip("/"))
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Make a request to the Copper API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            params: Query parameters
            json: Request body
            
        Returns:
            Union[Dict[str, Any], List[Dict[str, Any]]]: Response data
            
        Raises:
            aiohttp.ClientError: If the request fails
        """
        await self._ensure_session()
        url = self._build_url(endpoint)
        
        async with self.session.request(method, url, params=params, json=json) as response:
            response.raise_for_status()
            return await response.json()
    
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Make a GET request.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            Union[Dict[str, Any], List[Dict[str, Any]]]: Response data
        """
        return await self._request("GET", endpoint, params=params)
    
    async def post(
        self,
        endpoint: str,
        json: Dict[str, Any]
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Make a POST request.
        
        Args:
            endpoint: API endpoint path
            json: Request body
            
        Returns:
            Union[Dict[str, Any], List[Dict[str, Any]]]: Response data
        """
        return await self._request("POST", endpoint, json=json)
    
    async def put(
        self,
        endpoint: str,
        json: Dict[str, Any]
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Make a PUT request.
        
        Args:
            endpoint: API endpoint path
            json: Request body
            
        Returns:
            Union[Dict[str, Any], List[Dict[str, Any]]]: Response data
        """
        return await self._request("PUT", endpoint, json=json)
    
    async def delete(
        self,
        endpoint: str
    ) -> None:
        """Make a DELETE request.
        
        Args:
            endpoint: API endpoint path
        """
        await self._request("DELETE", endpoint) 