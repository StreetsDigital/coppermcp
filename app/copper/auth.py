"""Authentication utilities for Copper CRM API.

This module provides functions for handling authentication with the Copper CRM API.
It includes token validation, caching, and environment variable management.
"""
import os
import re
import time
from typing import Optional, Tuple, Dict, Any
from functools import lru_cache
from datetime import datetime, timedelta

class AuthenticationError(Exception):
    """Exception raised for authentication errors.
    
    Attributes:
        message: Error message
        env_var: The environment variable that caused the error
    """
    
    def __init__(self, message: str, env_var: Optional[str] = None):
        """Initialize the error.
        
        Args:
            message: Error message
            env_var: The environment variable that caused the error
        """
        super().__init__(message)
        self.message = message
        self.env_var = env_var

class TokenValidationError(AuthenticationError):
    """Exception raised for token validation errors."""
    pass

class TokenCache:
    """Cache for authentication tokens with expiration."""
    
    def __init__(self, ttl_seconds: int = 3600):
        """Initialize the token cache.
        
        Args:
            ttl_seconds: Time-to-live in seconds for cached tokens
        """
        self.cache: Dict[str, Any] = {}
        self.ttl_seconds = ttl_seconds
    
    def get(self, key: str) -> Optional[str]:
        """Get a token from the cache if not expired.
        
        Args:
            key: Cache key
            
        Returns:
            Optional[str]: The cached token if valid, None otherwise
        """
        if key not in self.cache:
            return None
            
        entry = self.cache[key]
        if time.time() > entry["expires_at"]:
            del self.cache[key]
            return None
            
        return entry["token"]
    
    def set(self, key: str, token: str) -> None:
        """Store a token in the cache.
        
        Args:
            key: Cache key
            token: Token to cache
        """
        self.cache[key] = {
            "token": token,
            "expires_at": time.time() + self.ttl_seconds
        }
    
    def clear(self) -> None:
        """Clear all cached tokens."""
        self.cache.clear()

# Global token cache instance
token_cache = TokenCache()

def validate_token(token: str) -> bool:
    """Validate token format.
    
    Args:
        token: Token to validate
        
    Returns:
        bool: True if token format is valid
        
    Raises:
        TokenValidationError: If token format is invalid
    """
    if not token:
        raise TokenValidationError("Token cannot be empty")
        
    # Check token length
    if len(token) < 32:
        raise TokenValidationError("Token is too short")
        
    # Check token format (alphanumeric)
    if not re.match(r'^[a-zA-Z0-9]+$', token):
        raise TokenValidationError("Token contains invalid characters")
        
    return True

def get_auth_token(env_var: str = "COPPER_API_TOKEN", use_cache: bool = True) -> str:
    """Get the Copper API authentication token.
    
    This function checks the cache first, then environment variables.
    It validates the token format before returning.
    
    Args:
        env_var: Environment variable name containing the token
        use_cache: Whether to use token caching
        
    Returns:
        str: The authentication token
        
    Raises:
        AuthenticationError: If the token is not found or invalid
    """
    # Check cache first
    if use_cache:
        cached_token = token_cache.get(env_var)
        if cached_token:
            return cached_token
    
    # Get from environment
    token = os.getenv(env_var)
    if not token:
        raise AuthenticationError(
            f"Copper API token not found. Please set the {env_var} environment variable.",
            env_var=env_var
        )
    
    # Validate token
    try:
        validate_token(token)
    except TokenValidationError as e:
        raise AuthenticationError(f"Invalid token format: {str(e)}", env_var=env_var)
    
    # Cache token
    if use_cache:
        token_cache.set(env_var, token)
    
    return token

def get_user_credentials(use_cache: bool = True) -> Tuple[str, str]:
    """Get the Copper user credentials from environment variables.
    
    This function checks the cache first, then environment variables.
    
    Args:
        use_cache: Whether to use credential caching
        
    Returns:
        Tuple[str, str]: A tuple containing (user_email, user_id)
        
    Raises:
        AuthenticationError: If either credential is not found or invalid
    """
    # Check cache first
    if use_cache:
        cached_email = token_cache.get("COPPER_USER_EMAIL")
        cached_id = token_cache.get("COPPER_USER_ID")
        if cached_email and cached_id:
            return cached_email, cached_id
    
    email = os.getenv("COPPER_USER_EMAIL")
    user_id = os.getenv("COPPER_USER_ID")
    
    if not email:
        raise AuthenticationError(
            "Copper user email not found. Please set the COPPER_USER_EMAIL environment variable.",
            env_var="COPPER_USER_EMAIL"
        )
    
    if not user_id:
        raise AuthenticationError(
            "Copper user ID not found. Please set the COPPER_USER_ID environment variable.",
            env_var="COPPER_USER_ID"
        )
    
    # Validate email format
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        raise AuthenticationError("Invalid email format", env_var="COPPER_USER_EMAIL")
    
    # Validate user ID format
    if not user_id.isdigit():
        raise AuthenticationError("User ID must be numeric", env_var="COPPER_USER_ID")
    
    # Cache credentials
    if use_cache:
        token_cache.set("COPPER_USER_EMAIL", email)
        token_cache.set("COPPER_USER_ID", user_id)
    
    return email, user_id

def get_auth_config(use_cache: bool = True) -> Dict[str, str]:
    """Get the complete authentication configuration.
    
    This function returns a complete set of validated credentials.
    
    Args:
        use_cache: Whether to use credential caching
        
    Returns:
        Dict[str, str]: Authentication configuration including token and user credentials
        
    Raises:
        AuthenticationError: If any required credentials are missing or invalid
    """
    token = get_auth_token(use_cache=use_cache)
    email, user_id = get_user_credentials(use_cache=use_cache)
    
    return {
        "token": token,
        "email": email,
        "user_id": user_id
    }

def clear_auth_cache() -> None:
    """Clear all cached authentication credentials."""
    token_cache.clear() 