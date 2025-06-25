"""
Response Formatter Utility for DaVinci Resolve MCP
Provides standardized response formats for API operations
"""

from typing import Any, Dict, Optional
import logging

logger = logging.getLogger("davinci-resolve-mcp.response")

def success(message: str, data: Optional[Any] = None, **extra) -> Dict[str, Any]:
    """
    Create a standardized success response.
    
    Args:
        message: Success message
        data: Optional data payload
        **extra: Additional key-value pairs to include
    
    Returns:
        Standardized success response dictionary
    """
    response = {
        "success": True,
        "message": message
    }
    
    if data is not None:
        response["data"] = data
    
    # Add any extra fields
    response.update(extra)
    
    logger.debug(f"Success response: {message}")
    return response

def error(message: str, error_code: Optional[str] = None, details: Optional[Any] = None, **extra) -> Dict[str, Any]:
    """
    Create a standardized error response.
    
    Args:
        message: Error message
        error_code: Optional error code for categorization
        details: Optional error details
        **extra: Additional key-value pairs to include
    
    Returns:
        Standardized error response dictionary
    """
    response = {
        "success": False,
        "message": message
    }
    
    if error_code:
        response["error_code"] = error_code
    
    if details is not None:
        response["details"] = details
    
    # Add any extra fields
    response.update(extra)
    
    logger.warning(f"Error response: {message}")
    return response

def info(message: str, data: Optional[Any] = None, **extra) -> Dict[str, Any]:
    """
    Create a standardized info response.
    
    Args:
        message: Info message
        data: Optional data payload
        **extra: Additional key-value pairs to include
    
    Returns:
        Standardized info response dictionary
    """
    response = {
        "success": True,
        "message": message,
        "type": "info"
    }
    
    if data is not None:
        response["data"] = data
    
    # Add any extra fields
    response.update(extra)
    
    logger.info(f"Info response: {message}")
    return response

# Legacy support for simple string returns
def legacy_success(message: str) -> str:
    """Return simple success string for backwards compatibility."""
    return f"Success: {message}"

def legacy_error(message: str) -> str:
    """Return simple error string for backwards compatibility."""
    return f"Error: {message}"
