"""
DaVinci Resolve MCP Server - Modular Architecture
Main server module that ties all API operations together
"""

import os
import sys
import logging
from typing import Optional

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import platform utilities
from src.utils.platform import setup_environment, get_platform, get_resolve_paths

# Setup platform-specific paths and environment variables
paths = get_resolve_paths()
RESOLVE_API_PATH = paths["api_path"]
RESOLVE_LIB_PATH = paths["lib_path"]
RESOLVE_MODULES_PATH = paths["modules_path"]

os.environ["RESOLVE_SCRIPT_API"] = RESOLVE_API_PATH
os.environ["RESOLVE_SCRIPT_LIB"] = RESOLVE_LIB_PATH

# Add the module path to Python's path if it's not already there
if RESOLVE_MODULES_PATH not in sys.path:
    sys.path.append(RESOLVE_MODULES_PATH)

# Import MCP
from mcp.server.fastmcp import FastMCP

# Configure logging
logger = logging.getLogger("davinci-resolve-mcp")

# Global resolve connection
resolve: Optional[object] = None

def initialize_resolve_connection():
    """Initialize connection to DaVinci Resolve."""
    global resolve
    try:
        # Direct import from the Modules directory
        sys.path.insert(0, RESOLVE_MODULES_PATH)
        import DaVinciResolveScript as dvr_script
        resolve = dvr_script.scriptapp("Resolve")
        if resolve:
            logger.info(f"Connected to DaVinci Resolve: {resolve.GetProductName()} {resolve.GetVersionString()}")
            return True
        else:
            logger.error("Failed to get Resolve object. Is DaVinci Resolve running?")
            return False
    except ImportError as e:
        logger.error(f"Failed to import DaVinciResolveScript: {str(e)}")
        logger.error("Check that DaVinci Resolve is installed and running.")
        logger.error(f"RESOLVE_SCRIPT_API: {RESOLVE_API_PATH}")
        logger.error(f"RESOLVE_SCRIPT_LIB: {RESOLVE_LIB_PATH}")
        logger.error(f"RESOLVE_MODULES_PATH: {RESOLVE_MODULES_PATH}")
        resolve = None
        return False
    except Exception as e:
        logger.error(f"Unexpected error initializing Resolve: {str(e)}")
        resolve = None
        return False

def create_mcp_server():
    """Create and configure the MCP server with all endpoints."""
    mcp = FastMCP("DaVinciResolveMCP")
    
    # Initialize resolve connection
    initialize_resolve_connection()
    
    # Register all API modules
    try:
        from src.api.core_operations import register_core_operations
        register_core_operations(mcp, resolve)
        logger.info("Registered core operations")
    except ImportError as e:
        logger.warning(f"Failed to import core operations: {e}")
    
    try:
        from src.api.project_operations import register_project_operations
        register_project_operations(mcp, resolve)
        logger.info("Registered project operations")
    except ImportError as e:
        logger.warning(f"Failed to import project operations: {e}")
    
    try:
        from src.api.timeline_operations import register_timeline_operations
        register_timeline_operations(mcp, resolve)
        logger.info("Registered timeline operations")
    except ImportError as e:
        logger.warning(f"Failed to import timeline operations: {e}")
    
    try:
        from src.api.media_operations import register_media_operations
        register_media_operations(mcp, resolve)
        logger.info("Registered media operations")
    except ImportError as e:
        logger.warning(f"Failed to import media operations: {e}")
    
    try:
        from src.api.color_operations import register_color_operations
        register_color_operations(mcp, resolve)
        logger.info("Registered color operations")
    except ImportError as e:
        logger.warning(f"Failed to import color operations: {e}")
    
    try:
        from src.api.delivery_operations import register_delivery_operations
        register_delivery_operations(mcp, resolve)
        logger.info("Registered delivery operations")
    except ImportError as e:
        logger.warning(f"Failed to import delivery operations: {e}")
    
    try:
        from src.api.fusion_operations import register_fusion_operations
        register_fusion_operations(mcp, resolve)
        logger.info("Registered fusion operations")
    except ImportError as e:
        logger.warning(f"Failed to import fusion operations: {e}")
    
    try:
        from src.api.fairlight_operations import register_fairlight_operations
        register_fairlight_operations(mcp, resolve)
        logger.info("Registered fairlight operations")
    except ImportError as e:
        logger.warning(f"Failed to import fairlight operations: {e}")
    
    try:
        from src.api.cache_management import register_cache_operations
        register_cache_operations(mcp, resolve)
        logger.info("Registered cache operations")
    except ImportError as e:
        logger.warning(f"Failed to import cache operations: {e}")
    
    try:
        from src.api.keyframe_control import register_keyframe_operations
        register_keyframe_operations(mcp, resolve)
        logger.info("Registered keyframe operations")
    except ImportError as e:
        logger.warning(f"Failed to import keyframe operations: {e}")
    
    try:
        from src.api.object_inspection import register_inspection_operations
        register_inspection_operations(mcp, resolve)
        logger.info("Registered inspection operations")
    except ImportError as e:
        logger.warning(f"Failed to import inspection operations: {e}")
    
    logger.info("DaVinci Resolve MCP Server ready to accept connections")
    return mcp

# For backwards compatibility, export the server instance
mcp = None

def get_server():
    """Get the MCP server instance (create if it doesn't exist)."""
    global mcp
    if mcp is None:
        mcp = create_mcp_server()
    return mcp

# Create server instance for direct import
mcp = create_mcp_server()
