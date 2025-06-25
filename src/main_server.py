#!/usr/bin/env python3
"""
DaVinci Resolve MCP Server - Main Entry Point
A server that connects to DaVinci Resolve via the Model Context Protocol (MCP)

Version: 1.4.0 - Modular Architecture
"""

import os
import sys
import logging
from typing import Optional

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

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

# Import operation modules
from src.api.core_operations import register_core_operations
from src.api.project_operations import register_project_operations
from src.api.timeline_operations import register_timeline_operations
from src.api.media_operations import register_media_operations
from src.api.color_operations import register_color_operations
from src.api.delivery_operations import register_delivery_operations
from src.api.fusion_operations import register_fusion_operations
from src.api.fairlight_operations import register_fairlight_operations
from src.api.cache_management import register_cache_operations
from src.api.keyframe_control import register_keyframe_operations
from src.api.object_inspection import register_inspection_operations

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("davinci-resolve-mcp")

# Log server version and platform
VERSION = "1.4.0"
logger.info(f"Starting DaVinci Resolve MCP Server v{VERSION}")
logger.info(f"Detected platform: {get_platform()}")
logger.info(f"Using Resolve API path: {RESOLVE_API_PATH}")
logger.info(f"Using Resolve library path: {RESOLVE_LIB_PATH}")

def initialize_resolve() -> Optional[object]:
    """Initialize connection to DaVinci Resolve."""
    try:
        # Direct import from the Modules directory
        sys.path.insert(0, RESOLVE_MODULES_PATH)
        import DaVinciResolveScript as dvr_script
        resolve = dvr_script.scriptapp("Resolve")
        if resolve:
            logger.info(f"Connected to DaVinci Resolve: {resolve.GetProductName()} {resolve.GetVersionString()}")
            return resolve
        else:
            logger.error("Failed to get Resolve object. Is DaVinci Resolve running?")
            return None
    except ImportError as e:
        logger.error(f"Failed to import DaVinciResolveScript: {str(e)}")
        logger.error("Check that DaVinci Resolve is installed and running.")
        logger.error(f"RESOLVE_SCRIPT_API: {RESOLVE_API_PATH}")
        logger.error(f"RESOLVE_SCRIPT_LIB: {RESOLVE_LIB_PATH}")
        logger.error(f"RESOLVE_MODULES_PATH: {RESOLVE_MODULES_PATH}")
        logger.error(f"sys.path: {sys.path}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error initializing Resolve: {str(e)}")
        return None

def create_server():
    """Create and configure the MCP server."""
    # Create MCP server instance
    mcp = FastMCP("DaVinciResolveMCP")
    
    # Initialize connection to DaVinci Resolve
    resolve = initialize_resolve()
    
    # Register all operation modules
    logger.info("Registering operation modules...")
    
    try:
        register_core_operations(mcp, resolve)
        logger.info("✓ Core operations registered")
        
        register_project_operations(mcp, resolve)
        logger.info("✓ Project operations registered")
        
        register_timeline_operations(mcp, resolve)
        logger.info("✓ Timeline operations registered")
        
        register_media_operations(mcp, resolve)
        logger.info("✓ Media operations registered")
        
        register_color_operations(mcp, resolve)
        logger.info("✓ Color operations registered")
        
        register_delivery_operations(mcp, resolve)
        logger.info("✓ Delivery operations registered")
        
        register_fusion_operations(mcp, resolve)
        logger.info("✓ Fusion operations registered")
        
        register_fairlight_operations(mcp, resolve)
        logger.info("✓ Fairlight operations registered")
        
        register_cache_operations(mcp, resolve)
        logger.info("✓ Cache management registered")
        
        register_keyframe_operations(mcp, resolve)
        logger.info("✓ Keyframe control registered")
        
        register_inspection_operations(mcp, resolve)
        logger.info("✓ Object inspection registered")
        
        logger.info("All operation modules registered successfully!")
        
    except Exception as e:
        logger.error(f"Error registering operations: {str(e)}")
        raise
    
    return mcp

def main():
    """Main entry point for the MCP server."""
    try:
        server = create_server()
        logger.info("DaVinci Resolve MCP Server ready!")
        return server
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise

if __name__ == "__main__":
    # For running the server directly
    server = main()
    # Note: In a real deployment, you'd call server.run() or similar
    # based on your MCP framework's requirements
