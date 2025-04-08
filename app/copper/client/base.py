"""Base client for Copper CRM API.

This module provides the base client class for interacting with the Copper CRM API.
It handles authentication, request building, and response parsing.
"""
import aiohttp
from typing import Dict, Any, Optional, List, Union, AsyncIterator
import asyncio
from urllib.parse import urljoin

class CopperAPIError(Exception):
    """Exception raised for Copper API errors.
    
    Attributes:
        status_code: HTTP status code
        message: Error message
        response: Raw response data
    """
    
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict[str, Any]] = None):
        """Initialize the error.
        
        Args:
            message: Error message
            status_code: HTTP status code
            response: Raw response data
        """
        super().__init__(message)
        self.status_code = status_code
        self.response = response
        self.message = message

class CopperClient:
    """Base client for Copper CRM API.
    
    This client supports:
    - Automatic session management via context manager
    - Request retries for transient failures
    - Configurable timeouts
    - Rate limiting compliance
    """
    
    BASE_URL = "https://api.copper.com/developer_api/v1/"
    DEFAULT_TIMEOUT = 30  # seconds
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds
    
    def __init__(
        self,
        auth_token: str,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        retry_delay: Optional[float] = None
    ):
        """Initialize the client.
        
        Args:
            auth_token: The authentication token for Copper API
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retries for failed requests (default: 3)
            retry_delay: Delay between retries in seconds (default: 1)
        """
        self.auth_token = auth_token
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.max_retries = max_retries or self.MAX_RETRIES
        self.retry_delay = retry_delay or self.RETRY_DELAY
        self.session = None
    
    async def __aenter__(self) -> 'CopperClient':
        """Enter the context manager."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context manager."""
        await self.close()
    
    async def _ensure_session(self) -> None:
        """Ensure an aiohttp session exists."""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(
                headers={
                    "X-PW-AccessToken": self.auth_token,
                    "X-PW-Application": "developer_api",
                    "Content-Type": "application/json"
                },
                timeout=timeout
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
        json: Optional[Dict[str, Any]] = None,
        retry_count: int = 0
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Make a request to the Copper API.
        
        This method handles retries for transient failures and rate limiting.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            params: Query parameters
            json: Request body
            retry_count: Current retry attempt number
            
        Returns:
            Union[Dict[str, Any], List[Dict[str, Any]]]: Response data
            
        Raises:
            CopperAPIError: If the request fails or returns an error
            aiohttp.ClientError: If there's a network or connection error
        """
        await self._ensure_session()
        url = self._build_url(endpoint)
        
        try:
            async with self.session.request(method, url, params=params, json=json) as response:
                response_data = await response.json() if response.content_type == "application/json" else None
                
                # Handle rate limiting
                if response.status == 429 and retry_count < self.max_retries:
                    retry_after = int(response.headers.get("Retry-After", self.retry_delay))
                    await asyncio.sleep(retry_after)
                    return await self._request(method, endpoint, params, json, retry_count + 1)
                
                # Handle other retryable errors
                if response.status >= 500 and retry_count < self.max_retries:
                    await asyncio.sleep(self.retry_delay * (retry_count + 1))
                    return await self._request(method, endpoint, params, json, retry_count + 1)
                
                if response.status >= 400:
                    message = str(response_data) if response_data else response.reason
                    raise CopperAPIError(
                        message=message,
                        status_code=response.status,
                        response=response_data
                    )
                
                return response_data
                
        except aiohttp.ClientError as e:
            if retry_count < self.max_retries:
                await asyncio.sleep(self.retry_delay * (retry_count + 1))
                return await self._request(method, endpoint, params, json, retry_count + 1)
            raise CopperAPIError(f"Request failed after {retry_count} retries: {str(e)}")
    
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
            
        Raises:
            CopperAPIError: If the request fails or returns an error
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
            
        Raises:
            CopperAPIError: If the request fails or returns an error
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
            
        Raises:
            CopperAPIError: If the request fails or returns an error
        """
        return await self._request("PUT", endpoint, json=json)
    
    async def delete(
        self,
        endpoint: str
    ) -> None:
        """Make a DELETE request.
        
        Args:
            endpoint: API endpoint path
            
        Raises:
            CopperAPIError: If the request fails or returns an error
        """
        await self._request("DELETE", endpoint) 