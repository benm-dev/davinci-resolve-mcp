"""
Core Operations Module
Handles basic DaVinci Resolve connection and page operations
"""

from typing import Optional

def register_core_operations(mcp, resolve: Optional[object]):
    """Register core DaVinci Resolve operations with the MCP server."""
    
    @mcp.resource("resolve://version")
    def get_resolve_version() -> str:
        """Get DaVinci Resolve version information."""
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        return f"{resolve.GetProductName()} {resolve.GetVersionString()}"

    @mcp.resource("resolve://current-page")
    def get_current_page() -> str:
        """Get the current page open in DaVinci Resolve (Edit, Color, Fusion, etc.)."""
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        return resolve.GetCurrentPage()

    @mcp.tool()
    def switch_page(page: str) -> str:
        """Switch to a specific page in DaVinci Resolve.
        
        Args:
            page: The page to switch to. Options: 'media', 'cut', 'edit', 'fusion', 'color', 'fairlight', 'deliver'
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        # Validate page name
        valid_pages = ['media', 'cut', 'edit', 'fusion', 'color', 'fairlight', 'deliver']
        if page.lower() not in valid_pages:
            return f"Error: Invalid page '{page}'. Valid pages are: {', '.join(valid_pages)}"
        
        try:
            result = resolve.OpenPage(page.lower())
            if result:
                return f"Successfully switched to {page} page"
            else:
                return f"Failed to switch to {page} page"
        except Exception as e:
            return f"Error switching to {page} page: {str(e)}"

    @mcp.tool()
    def get_product_info() -> str:
        """Get DaVinci Resolve product information."""
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        try:
            product_name = resolve.GetProductName()
            version = resolve.GetVersionString()
            return f"Product: {product_name}, Version: {version}"
        except Exception as e:
            return f"Error getting product info: {str(e)}"

    @mcp.resource("resolve://connection/status")
    def get_connection_status() -> dict:
        """Get the current connection status to DaVinci Resolve."""
        if resolve is None:
            return {
                "connected": False,
                "error": "Not connected to DaVinci Resolve"
            }
        
        try:
            product_name = resolve.GetProductName()
            version = resolve.GetVersionString()
            current_page = resolve.GetCurrentPage()
            
            return {
                "connected": True,
                "product_name": product_name,
                "version": version,
                "current_page": current_page
            }
        except Exception as e:
            return {
                "connected": False,
                "error": f"Connection error: {str(e)}"
            }

    @mcp.tool()
    def reconnect_to_resolve() -> str:
        """Attempt to reconnect to DaVinci Resolve."""
        try:
            import sys
            import os
            
            # Re-import DaVinci Resolve script
            from src.utils.platform import get_resolve_paths
            paths = get_resolve_paths()
            RESOLVE_MODULES_PATH = paths["modules_path"]
            
            sys.path.insert(0, RESOLVE_MODULES_PATH)
            import DaVinciResolveScript as dvr_script
            
            # Try to get a new connection
            new_resolve = dvr_script.scriptapp("Resolve")
            if new_resolve:
                # Update the global resolve object (this would need to be handled properly)
                return f"Successfully reconnected to DaVinci Resolve: {new_resolve.GetProductName()} {new_resolve.GetVersionString()}"
            else:
                return "Failed to reconnect. Is DaVinci Resolve running?"
                
        except Exception as e:
            return f"Error reconnecting to DaVinci Resolve: {str(e)}"
