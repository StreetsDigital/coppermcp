"""Authentication utilities for Copper CRM API.

This module provides functions for handling authentication with the Copper CRM API.
"""
import os
from typing import Optional, Tuple

def get_auth_token(env_var: str = "COPPER_API_TOKEN") -> str:
    """Get the Copper API authentication token.
    
    Args:
        env_var: Environment variable name containing the token
        
    Returns:
        str: The authentication token
        
    Raises:
        ValueError: If the token is not found in environment variables
    """
    token = os.getenv(env_var)
    if not token:
        raise ValueError(
            f"Copper API token not found. Please set the {env_var} environment variable."
        )
    return token

def get_user_credentials() -> Tuple[str, str]:
    """Get the Copper user credentials from environment variables.
    
    Returns:
        Tuple[str, str]: A tuple containing (user_email, user_id)
        
    Raises:
        ValueError: If either credential is not found in environment variables
    """
    email = os.getenv("COPPER_USER_EMAIL")
    user_id = os.getenv("COPPER_USER_ID")
    
    if not email:
        raise ValueError(
            "Copper user email not found. Please set the COPPER_USER_EMAIL environment variable."
        )
    
    if not user_id:
        raise ValueError(
            "Copper user ID not found. Please set the COPPER_USER_ID environment variable."
        )
    
    return email, user_id

def get_auth_config() -> dict:
    """Get the complete authentication configuration.
    
    Returns:
        dict: Authentication configuration including token and user credentials
        
    Raises:
        ValueError: If any required credentials are missing
    """
    token = get_auth_token()
    email, user_id = get_user_credentials()
    
    return {
        "token": token,
        "email": email,
        "user_id": user_id
    } 