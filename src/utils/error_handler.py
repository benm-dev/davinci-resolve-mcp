"""
Centralized Error Handler for DaVinci Resolve MCP
Provides standardized error handling and logging
"""

import logging
import traceback
from typing import Any, Dict, Optional, Callable
from functools import wraps
from .response_formatter import error

logger = logging.getLogger("davinci-resolve-mcp.error_handler")

class ResolveError(Exception):
    """Base exception for DaVinci Resolve operations."""
    pass

class ConnectionError(ResolveError):
    """Exception for connection-related errors."""
    pass

class ValidationError(ResolveError):
    """Exception for validation errors."""
    pass

class OperationError(ResolveError):
    """Exception for operation failures."""
    pass

def handle_resolve_errors(func: Callable) -> Callable:
    """
    Decorator to handle common DaVinci Resolve errors with standardized responses.
    
    Args:
        func: Function to wrap with error handling
    
    Returns:
        Wrapped function with error handling
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
            
        except ConnectionError as e:
            logger.error(f"Connection error in {func.__name__}: {str(e)}")
            return error(str(e), "CONNECTION_ERROR")
            
        except ValidationError as e:
            logger.warning(f"Validation error in {func.__name__}: {str(e)}")
            return error(str(e), "VALIDATION_ERROR")
            
        except OperationError as e:
            logger.error(f"Operation error in {func.__name__}: {str(e)}")
            return error(str(e), "OPERATION_ERROR")
            
        except Exception as e:
            # Log the full traceback for unexpected errors
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return error(f"Unexpected error: {str(e)}", "INTERNAL_ERROR")
            
    return wrapper

def log_operation(operation_name: str, details: Optional[Dict[str, Any]] = None) -> None:
    """
    Log an operation with optional details.
    
    Args:
        operation_name: Name of the operation being performed
        details: Optional details about the operation
    """
    if details:
        logger.info(f"Operation: {operation_name} - Details: {details}")
    else:
        logger.info(f"Operation: {operation_name}")

def validate_resolve_state(resolve: Any) -> None:
    """
    Validate that DaVinci Resolve is in a usable state.
    
    Args:
        resolve: DaVinci Resolve instance
    
    Raises:
        ConnectionError: If resolve is not properly connected
    """
    if resolve is None:
        raise ConnectionError("Not connected to DaVinci Resolve")
    
    try:
        # Test the connection with a simple operation
        resolve.GetCurrentPage()
    except Exception as e:
        raise ConnectionError(f"DaVinci Resolve connection error: {str(e)}")

def get_project_state(resolve: Any) -> Dict[str, Any]:
    """
    Get the current project state for error context.
    
    Args:
        resolve: DaVinci Resolve instance
    
    Returns:
        Dictionary with current project state
    """
    try:
        validate_resolve_state(resolve)
        
        project_manager = resolve.GetProjectManager()
        current_project = project_manager.GetCurrentProject() if project_manager else None
        current_timeline = current_project.GetCurrentTimeline() if current_project else None
        
        return {
            "has_project_manager": project_manager is not None,
            "has_current_project": current_project is not None,
            "has_current_timeline": current_timeline is not None,
            "current_page": resolve.GetCurrentPage(),
            "project_name": current_project.GetName() if current_project else None,
            "timeline_name": current_timeline.GetName() if current_timeline else None
        }
    except Exception as e:
        logger.warning(f"Could not get project state: {str(e)}")
        return {"error": str(e)}

def create_context_error(base_message: str, context: Dict[str, Any]) -> str:
    """
    Create an error message with context information.
    
    Args:
        base_message: Base error message
        context: Context information to include
    
    Returns:
        Enhanced error message with context
    """
    context_str = ", ".join([f"{k}={v}" for k, v in context.items() if v is not None])
    if context_str:
        return f"{base_message} (Context: {context_str})"
    return base_message
