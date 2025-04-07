"""Base client for making HTTP requests to the Copper API.

This module provides the base client class that handles authentication and HTTP requests.
"""

import json
from typing import Optional, Dict, Any, Union
import requests


class CopperBaseClient:
    """Base client for making HTTP requests to the Copper API."""
    
    def __init__(
        self,
        api_key: str,
        email: str,
        base_url: str = "https://api.copper.com/developer_api/v1"
    ):
        """Initialize the base client.
        
        Args:
            api_key: Copper API key
            email: Copper user email
            base_url: Base URL for the Copper API
        """
        self.api_key = api_key
        self.email = email
        self.base_url = base_url.rstrip('/')
        
        self.session = requests.Session()
        self.session.headers.update({
            'X-PW-AccessToken': self.api_key,
            'X-PW-Application': 'developer_api',
            'X-PW-UserEmail': self.email,
            'Content-Type': 'application/json'
        })
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any
    ) -> Union[Dict[str, Any], list]:
        """Make an HTTP request to the Copper API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Response data as dict or list
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            if response.content:
                return response.json()
            return {}
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.content:
                error_data = e.response.json()
                error_message = error_data.get('message', str(e))
                raise requests.exceptions.HTTPError(
                    f"{e.response.status_code} {e.response.reason}: {error_message}",
                    response=e.response
                ) from None
            raise
    
    def _get(self, endpoint: str, **kwargs: Any) -> Union[Dict[str, Any], list]:
        """Make a GET request.
        
        Args:
            endpoint: API endpoint
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Response data
        """
        return self._make_request('GET', endpoint, **kwargs)
    
    def _post(self, endpoint: str, **kwargs: Any) -> Union[Dict[str, Any], list]:
        """Make a POST request.
        
        Args:
            endpoint: API endpoint
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Response data
        """
        return self._make_request('POST', endpoint, **kwargs)
    
    def _put(self, endpoint: str, **kwargs: Any) -> Union[Dict[str, Any], list]:
        """Make a PUT request.
        
        Args:
            endpoint: API endpoint
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Response data
        """
        return self._make_request('PUT', endpoint, **kwargs)
    
    def _delete(self, endpoint: str, **kwargs: Any) -> Union[Dict[str, Any], list]:
        """Make a DELETE request.
        
        Args:
            endpoint: API endpoint
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Response data
        """
        return self._make_request('DELETE', endpoint, **kwargs) 