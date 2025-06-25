"""
Page Manager Utility for DaVinci Resolve MCP
Ensures the correct Resolve page is active for an operation and restores the previous page after.
"""

import logging
from functools import wraps
from typing import Any, Callable, Optional

logger = logging.getLogger("davinci-resolve-mcp.page_manager")

def ensure_page(page_name: str):
    """
    Decorator to ensure the specified Resolve page is active during the function call.
    Restores the previous page after the function completes.

    Args:
        page_name: The page to switch to (fusion, color, edit, etc.)

    Usage:
        @ensure_page("fusion")
        def my_fusion_op(resolve, ...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract resolve object from function signature
            resolve = _extract_resolve_object(func, args, kwargs)
            if not resolve:
                error_msg = f"Could not find 'resolve' object for function {func.__name__}"
                logger.error(error_msg)
                return {"error": error_msg}

            # Get current page and switch if needed
            try:
                current_page = resolve.GetCurrentPage()
                logger.debug(f"Current page: {current_page}, target page: {page_name}")

                page_switched = False
                if current_page.lower() != page_name.lower():
                    result = resolve.OpenPage(page_name)
                    if not result:
                        error_msg = f"Failed to switch to {page_name} page"
                        logger.error(error_msg)
                        return {"error": error_msg}
                    page_switched = True
                    logger.debug(f"Switched from {current_page} to {page_name}")

                # Execute the function
                try:
                    return func(*args, **kwargs)
                finally:
                    # Always restore the original page if we switched
                    if page_switched:
                        try:
                            resolve.OpenPage(current_page)
                            logger.debug(f"Restored page to {current_page}")
                        except Exception as e:
                            logger.warning(f"Failed to restore page to {current_page}: {str(e)}")

            except Exception as e:
                error_msg = f"Error in page management for {func.__name__}: {str(e)}"
                logger.error(error_msg)
                return {"error": error_msg}

        return wrapper
    return decorator

def _extract_resolve_object(func: Callable, args: tuple, kwargs: dict) -> Optional[Any]:
    """Extract the resolve object from function arguments."""
    # First try kwargs
    resolve = kwargs.get("resolve")
    if resolve:
        return resolve

    # Then try first positional argument
    if args and hasattr(args[0], 'GetCurrentPage'):
        return args[0]

    # Check if it's in a nested structure (for MCP registered functions)
    if len(args) > 1 and hasattr(args[1], 'GetCurrentPage'):
        return args[1]

    return None

def get_valid_pages() -> list:
    """Get list of valid DaVinci Resolve pages."""
    return ['media', 'cut', 'edit', 'fusion', 'color', 'fairlight', 'deliver']

def validate_page_name(page_name: str) -> bool:
    """Validate that a page name is valid."""
    return page_name.lower() in get_valid_pages()
