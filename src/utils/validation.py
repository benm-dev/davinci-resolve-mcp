"""
Input Validation Utilities for DaVinci Resolve MCP
Provides common validation functions and decorators
"""

import os
from functools import wraps
from typing import Any, Callable, List, Union, Optional, Dict
import logging

logger = logging.getLogger("davinci-resolve-mcp.validation")

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

def validate_range(value: Union[int, float], min_val: Union[int, float], max_val: Union[int, float], name: str = "value") -> None:
    """
    Validate that a numeric value is within a specified range.
    
    Args:
        value: The value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        name: Name of the parameter for error messages
    
    Raises:
        ValidationError: If value is outside the range
    """
    if not isinstance(value, (int, float)):
        raise ValidationError(f"{name} must be a number, got {type(value).__name__}")
    
    if value < min_val or value > max_val:
        raise ValidationError(f"{name} must be between {min_val} and {max_val}, got {value}")

def validate_choice(value: str, choices: List[str], name: str = "value", case_sensitive: bool = False) -> str:
    """
    Validate that a string value is one of the allowed choices.
    
    Args:
        value: The value to validate
        choices: List of allowed values
        name: Name of the parameter for error messages
        case_sensitive: Whether comparison should be case-sensitive
    
    Returns:
        The validated value (potentially normalized)
    
    Raises:
        ValidationError: If value is not in choices
    """
    if not isinstance(value, str):
        raise ValidationError(f"{name} must be a string, got {type(value).__name__}")
    
    if case_sensitive:
        if value not in choices:
            raise ValidationError(f"{name} must be one of {choices}, got '{value}'")
        return value
    else:
        # Case-insensitive comparison
        value_lower = value.lower()
        choices_lower = [choice.lower() for choice in choices]
        
        if value_lower not in choices_lower:
            raise ValidationError(f"{name} must be one of {choices}, got '{value}'")
        
        # Return the original case from choices
        index = choices_lower.index(value_lower)
        return choices[index]

def validate_file_path(path: str, must_exist: bool = True, name: str = "file_path") -> None:
    """
    Validate a file path.
    
    Args:
        path: The file path to validate
        must_exist: Whether the file must already exist
        name: Name of the parameter for error messages
    
    Raises:
        ValidationError: If path is invalid
    """
    if not isinstance(path, str):
        raise ValidationError(f"{name} must be a string, got {type(path).__name__}")
    
    if not path.strip():
        raise ValidationError(f"{name} cannot be empty")
    
    if must_exist and not os.path.exists(path):
        raise ValidationError(f"{name} does not exist: {path}")
    
    if must_exist and not os.path.isfile(path):
        raise ValidationError(f"{name} is not a file: {path}")

def validate_directory_path(path: str, must_exist: bool = True, name: str = "directory_path") -> None:
    """
    Validate a directory path.
    
    Args:
        path: The directory path to validate
        must_exist: Whether the directory must already exist
        name: Name of the parameter for error messages
    
    Raises:
        ValidationError: If path is invalid
    """
    if not isinstance(path, str):
        raise ValidationError(f"{name} must be a string, got {type(path).__name__}")
    
    if not path.strip():
        raise ValidationError(f"{name} cannot be empty")
    
    if must_exist and not os.path.exists(path):
        raise ValidationError(f"{name} does not exist: {path}")
    
    if must_exist and not os.path.isdir(path):
        raise ValidationError(f"{name} is not a directory: {path}")

def validate_file_extension(path: str, allowed_extensions: List[str], name: str = "file_path") -> None:
    """
    Validate that a file has one of the allowed extensions.
    
    Args:
        path: The file path to validate
        allowed_extensions: List of allowed extensions (with or without dots)
        name: Name of the parameter for error messages
    
    Raises:
        ValidationError: If file extension is not allowed
    """
    if not isinstance(path, str):
        raise ValidationError(f"{name} must be a string, got {type(path).__name__}")
    
    # Normalize extensions to include dots
    normalized_extensions = []
    for ext in allowed_extensions:
        if not ext.startswith('.'):
            ext = '.' + ext
        normalized_extensions.append(ext.lower())
    
    file_extension = os.path.splitext(path)[1].lower()
    
    if file_extension not in normalized_extensions:
        raise ValidationError(f"{name} must have one of these extensions: {allowed_extensions}, got '{file_extension}'")

def validate_resolve_connection(resolve: Any, name: str = "resolve") -> None:
    """
    Validate that resolve connection is active.
    
    Args:
        resolve: The resolve object to validate
        name: Name of the parameter for error messages
    
    Raises:
        ValidationError: If resolve is not connected
    """
    if resolve is None:
        raise ValidationError("Not connected to DaVinci Resolve")
    
    # Try to access a basic method to verify connection
    try:
        resolve.GetCurrentPage()
    except Exception as e:
        raise ValidationError(f"DaVinci Resolve connection error: {str(e)}")

def validate_positive_integer(value: int, name: str = "value") -> None:
    """
    Validate that a value is a positive integer.
    
    Args:
        value: The value to validate
        name: Name of the parameter for error messages
    
    Raises:
        ValidationError: If value is not a positive integer
    """
    if not isinstance(value, int):
        raise ValidationError(f"{name} must be an integer, got {type(value).__name__}")
    
    if value <= 0:
        raise ValidationError(f"{name} must be positive, got {value}")

def validate_non_empty_string(value: str, name: str = "value") -> None:
    """
    Validate that a value is a non-empty string.
    
    Args:
        value: The value to validate
        name: Name of the parameter for error messages
    
    Raises:
        ValidationError: If value is not a non-empty string
    """
    if not isinstance(value, str):
        raise ValidationError(f"{name} must be a string, got {type(value).__name__}")
    
    if not value.strip():
        raise ValidationError(f"{name} cannot be empty")

# Decorator for validating function parameters
def validate_params(**validators) -> Callable:
    """
    Decorator to validate function parameters using specified validators.
    
    Args:
        **validators: Dictionary mapping parameter names to validation functions
    
    Usage:
        @validate_params(
            opacity=lambda x: validate_range(x, 0.0, 1.0, "opacity"),
            blend_mode=lambda x: validate_choice(x, ["Normal", "Add", "Multiply"], "blend_mode")
        )
        def my_function(opacity, blend_mode):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature to map args to parameter names
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Validate parameters
            for param_name, validator in validators.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    try:
                        validator(value)
                    except ValidationError as e:
                        logger.error(f"Validation error in {func.__name__}: {str(e)}")
                        return {"error": f"Invalid {param_name}: {str(e)}"}
                    except Exception as e:
                        logger.error(f"Unexpected validation error in {func.__name__}: {str(e)}")
                        return {"error": f"Validation error for {param_name}: {str(e)}"}
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
