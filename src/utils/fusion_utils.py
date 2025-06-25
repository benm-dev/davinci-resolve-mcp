"""
Fusion Utilities for DaVinci Resolve MCP
Provides standardized utilities for Fusion node operations
"""

import logging
from typing import Any, Dict, List, Optional, Union
from .response_formatter import success, error
from .validation import ValidationError, validate_resolve_connection, validate_non_empty_string

logger = logging.getLogger("davinci-resolve-mcp.fusion_utils")

class FusionNodeError(Exception):
    """Custom exception for Fusion node operations."""
    pass

def get_fusion_comp(resolve: Any) -> Any:
    """
    Get the current Fusion composition with error handling.
    
    Args:
        resolve: DaVinci Resolve instance
    
    Returns:
        Fusion composition object
    
    Raises:
        FusionNodeError: If composition cannot be accessed
    """
    validate_resolve_connection(resolve)
    
    try:
        fusion = resolve.Fusion()
        if not fusion:
            raise FusionNodeError("Failed to access Fusion")
        
        comp = fusion.GetCurrentComp()
        if not comp:
            raise FusionNodeError("No Fusion composition active")
        
        return comp
    except Exception as e:
        if isinstance(e, FusionNodeError):
            raise
        raise FusionNodeError(f"Error accessing Fusion composition: {str(e)}")

def set_node_input(node: Any, input_name: str, value: Any) -> bool:
    """
    Safely set a node input using the standardized method.
    
    Args:
        node: Fusion node object
        input_name: Name of the input parameter
        value: Value to set
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Try the modern SetInput method first
        if hasattr(node, 'SetInput'):
            node.SetInput(input_name, value)
            return True
        
        # Fall back to direct attribute access for older APIs
        input_obj = getattr(node, input_name, None)
        if input_obj and hasattr(input_obj, '__setitem__'):
            if isinstance(value, (list, tuple)):
                for i, v in enumerate(value):
                    input_obj[i] = v
            else:
                input_obj[0] = value
            return True
        
        logger.warning(f"Could not set input '{input_name}' on node")
        return False
        
    except Exception as e:
        logger.error(f"Error setting node input '{input_name}': {str(e)}")
        return False

def set_node_attributes(node: Any, attributes: Dict[str, Any]) -> bool:
    """
    Safely set node attributes using SetAttrs.
    
    Args:
        node: Fusion node object
        attributes: Dictionary of attributes to set
    
    Returns:
        True if successful, False otherwise
    """
    try:
        node.SetAttrs(attributes)
        return True
    except Exception as e:
        logger.error(f"Error setting node attributes: {str(e)}")
        return False

def find_node(comp: Any, node_name: str) -> Optional[Any]:
    """
    Find a node in the composition by name.
    
    Args:
        comp: Fusion composition object
        node_name: Name of the node to find
    
    Returns:
        Node object if found, None otherwise
    """
    try:
        return comp.FindTool(node_name)
    except Exception as e:
        logger.error(f"Error finding node '{node_name}': {str(e)}")
        return None

def get_node_info(node: Any) -> Dict[str, Any]:
    """
    Get comprehensive information about a Fusion node.
    
    Args:
        node: Fusion node object
    
    Returns:
        Dictionary with node information
    """
    try:
        attrs = node.GetAttrs()
        return {
            "name": attrs.get("TOOLS_Name", "Unknown"),
            "type": attrs.get("TOOLS_RegID", "Unknown"),
            "id": attrs.get("TOOLS_ID", "Unknown"),
            "pos_x": attrs.get("TOOLNT_Position_X", 0),
            "pos_y": attrs.get("TOOLNT_Position_Y", 0),
            "selected": attrs.get("TOOLB_Selected", False),
            "locked": attrs.get("TOOLB_Locked", False),
            "pass_through": attrs.get("TOOLB_PassThrough", False)
        }
    except Exception as e:
        logger.error(f"Error getting node info: {str(e)}")
        return {"error": str(e)}

def connect_nodes(comp: Any, source_name: str, target_name: str, 
                 source_output: str = "Output", target_input: str = "Input") -> Dict[str, Any]:
    """
    Connect two nodes in the Fusion composition using standardized error handling.
    
    Args:
        comp: Fusion composition object
        source_name: Name of the source node
        target_name: Name of the target node
        source_output: Output connector name
        target_input: Input connector name
    
    Returns:
        Standardized response dictionary
    """
    try:
        # Find the nodes
        source_node = find_node(comp, source_name)
        if not source_node:
            return error(f"Source node '{source_name}' not found", "NODE_NOT_FOUND")
        
        target_node = find_node(comp, target_name)
        if not target_node:
            return error(f"Target node '{target_name}' not found", "NODE_NOT_FOUND")
        
        # Try modern connection method first
        try:
            target_input_obj = target_node.FindMainInput(target_input)
            source_output_obj = source_node.FindMainOutput(source_output)
            
            if target_input_obj and source_output_obj:
                target_input_obj.ConnectTo(source_output_obj)
            else:
                # Fall back to older method
                target_node.ConnectInput(target_input, source_node)
        except:
            # Fall back to older method
            target_node.ConnectInput(target_input, source_node)
        
        return success(f"Connected {source_name}.{source_output} to {target_name}.{target_input}")
        
    except Exception as e:
        return error(f"Error connecting nodes: {str(e)}", "CONNECTION_ERROR")

def validate_node_type(node_type: str) -> bool:
    """
    Validate that a node type is potentially valid for Fusion.
    
    Args:
        node_type: The node type string to validate
    
    Returns:
        True if valid, False otherwise
    """
    # Basic validation - node types should be non-empty strings
    if not isinstance(node_type, str) or not node_type.strip():
        return False
    
    # Common invalid characters in node types
    invalid_chars = [' ', '\t', '\n', '/', '\\', ':', ';', ',']
    if any(char in node_type for char in invalid_chars):
        return False
    
    return True

def get_available_blend_modes() -> Dict[str, int]:
    """Get mapping of blend mode names to their numeric values."""
    return {
        "Normal": 0,
        "Add": 1,
        "Multiply": 2,
        "Screen": 3,
        "Overlay": 4,
        "SoftLight": 5,
        "HardLight": 6,
        "Darken": 7,
        "Lighten": 8,
        "Difference": 9,
        "Exclusion": 10,
        "ColorDodge": 11,
        "ColorBurn": 12
    }

def validate_blend_mode(blend_mode: str) -> str:
    """
    Validate and normalize a blend mode.
    
    Args:
        blend_mode: The blend mode to validate
    
    Returns:
        Normalized blend mode name
    
    Raises:
        ValidationError: If blend mode is invalid
    """
    available_modes = get_available_blend_modes()
    
    # Case-insensitive lookup
    for mode_name in available_modes.keys():
        if blend_mode.lower() == mode_name.lower():
            return mode_name
    
    raise ValidationError(f"Invalid blend mode '{blend_mode}'. Available modes: {list(available_modes.keys())}")

def get_node_categories() -> Dict[str, List[str]]:
    """Get categorized list of common Fusion node types."""
    return {
        "generators": [
            "Background", "Checkerboard", "Ellipse", "Noise", "Plasma",
            "Rectangle", "Text+", "TextPlus", "WaveForm"
        ],
        "color_correction": [
            "BrightnessContrast", "ChannelBooleans", "ColorCorrector",
            "ColorCurves", "Gamma", "Hue", "Saturation"
        ],
        "composite": [
            "AlphaMultiply", "AlphaDivide", "Merge", "Over", "Under",
            "Add", "Multiply", "Screen", "Overlay"
        ],
        "transform": [
            "Transform", "DVE", "CornerPin", "GridWarp", "LensDistortion",
            "Perspective", "Resize", "Crop"
        ],
        "filters": [
            "Blur", "Sharpen", "Glow", "SoftGlow", "UnsharpMask",
            "Despill", "Emboss", "Sobel", "Erode", "Dilate"
        ],
        "keying": [
            "ChromaKeyer", "LumaKeyer", "ColorKeyer", "DeltaKeyer",
            "Primatte", "UltraKeyer"
        ],
        "3d": [
            "Renderer3D", "Camera3D", "ImagePlane3D", "Merge3D",
            "Shape3D", "Spotlight3D", "Transform3D"
        ],
        "particles": [
            "pEmitter", "pRender", "pBounce", "pDirectionalForce",
            "pGravity", "pKill", "pSpawn", "pTurbulence"
        ]
    }
