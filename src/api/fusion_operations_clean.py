"""
Fusion Operations Module
Handles DaVinci Resolve Fusion page operations and detailed effects
Comprehensive visual effects and compositing capabilities
"""

from typing import Optional, Dict, Any, List, Union
import logging

# Import utilities
from ..utils.page_manager import ensure_page
from ..utils.response_formatter import success, error, info
from ..utils.validation import (
    validate_range, validate_choice, validate_non_empty_string,
    validate_resolve_connection, ValidationError
)
from ..utils.fusion_utils import (
    get_fusion_comp, set_node_input, set_node_attributes,
    find_node, get_node_info, connect_nodes, validate_node_type,
    validate_blend_mode, get_available_blend_modes, get_node_categories
)

logger = logging.getLogger("davinci-resolve-mcp.fusion")

def register_fusion_operations(mcp, resolve: Optional[object]):
    """Register comprehensive Fusion page operations with the MCP server."""

    # ------------------
    # Core Node Operations
    # ------------------

    @mcp.resource("resolve://fusion/composition")
    @ensure_page("fusion")
    def get_fusion_composition() -> Dict[str, Any]:
        """Get information about the current Fusion composition."""
        try:
            validate_resolve_connection(resolve)
            comp = get_fusion_comp(resolve)
            
            comp_attrs = comp.GetAttrs()
            comp_info = {
                "name": comp_attrs.get("COMPN_Name", "Unknown"),
                "frame_start": comp_attrs.get("COMPN_GlobalStart", 0),
                "frame_end": comp_attrs.get("COMPN_GlobalEnd", 0),
                "current_time": comp.CurrentTime,
                "render_start": comp_attrs.get("COMPN_RenderStart", 0),
                "render_end": comp_attrs.get("COMPN_RenderEnd", 0),
                "fps": comp_attrs.get("COMPN_FrameRate", 24.0),
                "resolution": {
                    "width": comp_attrs.get("COMPN_ImageWidth", 1920),
                    "height": comp_attrs.get("COMPN_ImageHeight", 1080),
                    "aspect": comp_attrs.get("COMPN_ImageAspect", 1.0)
                }
            }
            
            return info("Fusion composition info retrieved", comp_info)
            
        except Exception as e:
            return error(f"Error accessing Fusion composition: {str(e)}")

    @mcp.resource("resolve://fusion/nodes")
    @ensure_page("fusion")
    def get_fusion_nodes() -> List[Dict[str, Any]]:
        """Get all nodes in the current Fusion composition."""
        try:
            validate_resolve_connection(resolve)
            comp = get_fusion_comp(resolve)
            
            nodes = []
            tool_list = comp.GetToolList()
            
            for name, tool in tool_list.items():
                node_info = get_node_info(tool)
                nodes.append(node_info)
            
            return success(f"Retrieved {len(nodes)} Fusion nodes", nodes)
            
        except Exception as e:
            return error(f"Error getting Fusion nodes: {str(e)}")

    @mcp.tool()
    @ensure_page("fusion")
    def add_fusion_node(node_type: str, name: str = None, pos_x: float = 0, pos_y: float = 0) -> Dict[str, Any]:
        """Add a new node to the Fusion composition.

        Args:
            node_type: Type of node to add (e.g., 'Transform', 'Merge', 'ColorCorrector')
            name: Optional custom name for the node
            pos_x: X position in the flow area
            pos_y: Y position in the flow area
        """
        try:
            validate_resolve_connection(resolve)
            validate_non_empty_string(node_type, "node_type")
            
            if not validate_node_type(node_type):
                return error(f"Invalid node type: {node_type}")
            
            comp = get_fusion_comp(resolve)
            
            # Add the node
            node = comp.AddTool(node_type)
            if not node:
                return error(f"Failed to create node of type '{node_type}'. Check if node type is valid.")
            
            # Set custom name if provided
            attributes = {}
            if name:
                validate_non_empty_string(name, "name")
                attributes["TOOLS_Name"] = name
            
            # Set position
            if pos_x != 0 or pos_y != 0:
                attributes.update({
                    "TOOLNT_Position_X": pos_x,
                    "TOOLNT_Position_Y": pos_y
                })
            
            if attributes:
                set_node_attributes(node, attributes)
            
            node_name = node.GetAttrs().get("TOOLS_Name", node_type)
            return success(f"Added {node_type} node: {node_name}", {"node_name": node_name, "node_type": node_type})
            
        except ValidationError as e:
            return error(str(e), "VALIDATION_ERROR")
        except Exception as e:
            return error(f"Error adding Fusion node: {str(e)}")

    @mcp.tool()
    @ensure_page("fusion")
    def connect_fusion_nodes(source_node: str, target_node: str,
                           source_output: str = "Output", target_input: str = "Input") -> Dict[str, Any]:
        """Connect two nodes in the Fusion composition.

        Args:
            source_node: Name of the source node
            target_node: Name of the target node
            source_output: Output connector name (default: "Output")
            target_input: Input connector name (default: "Input")
        """
        try:
            validate_resolve_connection(resolve)
            validate_non_empty_string(source_node, "source_node")
            validate_non_empty_string(target_node, "target_node")
            
            comp = get_fusion_comp(resolve)
            return connect_nodes(comp, source_node, target_node, source_output, target_input)
            
        except ValidationError as e:
            return error(str(e), "VALIDATION_ERROR")
        except Exception as e:
            return error(f"Error connecting Fusion nodes: {str(e)}")

    @mcp.tool()
    @ensure_page("fusion")
    def delete_fusion_node(node_name: str) -> Dict[str, Any]:
        """Delete a node from the Fusion composition.

        Args:
            node_name: Name of the node to delete
        """
        try:
            validate_resolve_connection(resolve)
            validate_non_empty_string(node_name, "node_name")
            
            comp = get_fusion_comp(resolve)
            
            # Find and delete the node
            node = find_node(comp, node_name)
            if not node:
                return error(f"Node '{node_name}' not found", "NODE_NOT_FOUND")
            
            node.Delete()
            return success(f"Deleted node: {node_name}")
            
        except ValidationError as e:
            return error(str(e), "VALIDATION_ERROR")
        except Exception as e:
            return error(f"Error deleting Fusion node: {str(e)}")

    # ------------------
    # Transform & Geometry
    # ------------------

    @mcp.tool()
    @ensure_page("fusion")
    def add_transform_node(name: str = None, center_x: float = 0.5, center_y: float = 0.5,
                          angle: float = 0, size: float = 1.0) -> Dict[str, Any]:
        """Add a Transform node with specified parameters.

        Args:
            name: Optional custom name for the node
            center_x: X center position (0.0 to 1.0)
            center_y: Y center position (0.0 to 1.0)
            angle: Rotation angle in degrees
            size: Scale factor
        """
        try:
            validate_resolve_connection(resolve)
            validate_range(center_x, 0.0, 1.0, "center_x")
            validate_range(center_y, 0.0, 1.0, "center_y")
            validate_range(size, 0.1, 10.0, "size")
            
            comp = get_fusion_comp(resolve)
            
            transform = comp.AddTool("Transform")
            if not transform:
                return error("Failed to create Transform node")
            
            # Set transform parameters using standardized method
            set_node_input(transform, "Center", [center_x, center_y])
            set_node_input(transform, "Angle", angle)
            set_node_input(transform, "Size", size)
            
            # Set custom name if provided
            if name:
                validate_non_empty_string(name, "name")
                set_node_attributes(transform, {"TOOLS_Name": name})
            
            node_name = transform.GetAttrs().get("TOOLS_Name", "Transform")
            return success(f"Added Transform node: {node_name}", {
                "node_name": node_name,
                "center": [center_x, center_y],
                "angle": angle,
                "size": size
            })
            
        except ValidationError as e:
            return error(str(e), "VALIDATION_ERROR")
        except Exception as e:
            return error(f"Error adding Transform node: {str(e)}")

    @mcp.tool()
    @ensure_page("fusion")
    def add_merge_node(name: str = None, blend_mode: str = "Normal",
                      opacity: float = 1.0) -> Dict[str, Any]:
        """Add a Merge node for compositing layers.

        Args:
            name: Optional custom name for the node
            blend_mode: Blend mode (Normal, Add, Multiply, Screen, etc.)
            opacity: Opacity value (0.0 to 1.0)
        """
        try:
            validate_resolve_connection(resolve)
            validate_range(opacity, 0.0, 1.0, "opacity")
            normalized_blend_mode = validate_blend_mode(blend_mode)
            
            comp = get_fusion_comp(resolve)
            
            merge = comp.AddTool("Merge")
            if not merge:
                return error("Failed to create Merge node")
            
            # Set blend mode and opacity
            blend_modes = get_available_blend_modes()
            set_node_input(merge, "Operator", blend_modes[normalized_blend_mode])
            set_node_input(merge, "Blend", opacity)
            
            # Set custom name if provided
            if name:
                validate_non_empty_string(name, "name")
                set_node_attributes(merge, {"TOOLS_Name": name})
            
            node_name = merge.GetAttrs().get("TOOLS_Name", "Merge")
            return success(f"Added Merge node: {node_name}", {
                "node_name": node_name,
                "blend_mode": normalized_blend_mode,
                "opacity": opacity
            })
            
        except ValidationError as e:
            return error(str(e), "VALIDATION_ERROR")
        except Exception as e:
            return error(f"Error adding Merge node: {str(e)}")

    @mcp.tool()
    @ensure_page("fusion")
    def add_text_node(name: str = None, text: str = "Sample Text",
                     font: str = "Arial", size: float = 0.1) -> Dict[str, Any]:
        """Add a Text+ node for text creation.

        Args:
            name: Optional custom name for the node
            text: Text content
            font: Font name
            size: Text size (0.0 to 1.0)
        """
        try:
            validate_resolve_connection(resolve)
            validate_non_empty_string(text, "text")
            validate_range(size, 0.01, 1.0, "size")
            
            comp = get_fusion_comp(resolve)
            
            text_node = comp.AddTool("TextPlus")
            if not text_node:
                return error("Failed to create Text+ node")
            
            # Set text properties
            set_node_input(text_node, "StyledText", text)
            set_node_input(text_node, "Font", font)
            set_node_input(text_node, "Size", size)
            
            # Set custom name if provided
            if name:
                validate_non_empty_string(name, "name")
                set_node_attributes(text_node, {"TOOLS_Name": name})
            
            node_name = text_node.GetAttrs().get("TOOLS_Name", "Text+")
            return success(f"Added Text+ node: {node_name}", {
                "node_name": node_name,
                "text": text,
                "font": font,
                "size": size
            })
            
        except ValidationError as e:
            return error(str(e), "VALIDATION_ERROR")
        except Exception as e:
            return error(f"Error adding Text+ node: {str(e)}")

    @mcp.tool()
    @ensure_page("fusion")
    def add_background_node(name: str = None, color: List[float] = None) -> Dict[str, Any]:
        """Add a Background generator node.

        Args:
            name: Optional custom name for the node
            color: RGBA color values (0.0 to 1.0) [R, G, B, A]
        """
        try:
            validate_resolve_connection(resolve)
            
            if color is None:
                color = [0.0, 0.0, 0.0, 1.0]  # Default black
            
            if len(color) != 4:
                return error("Color must be a list of 4 values [R, G, B, A]")
            
            for i, component in enumerate(color):
                validate_range(component, 0.0, 1.0, f"color[{i}]")
            
            comp = get_fusion_comp(resolve)
            
            background = comp.AddTool("Background")
            if not background:
                return error("Failed to create Background node")
            
            # Set background color
            set_node_input(background, "TopLeftColor", color)
            
            # Set custom name if provided
            if name:
                validate_non_empty_string(name, "name")
                set_node_attributes(background, {"TOOLS_Name": name})
            
            node_name = background.GetAttrs().get("TOOLS_Name", "Background")
            return success(f"Added Background node: {node_name}", {
                "node_name": node_name,
                "color": color
            })
            
        except ValidationError as e:
            return error(str(e), "VALIDATION_ERROR")
        except Exception as e:
            return error(f"Error adding Background node: {str(e)}")

    @mcp.tool()
    @ensure_page("fusion")
    def set_node_parameter(node_name: str, parameter: str, value: Any) -> Dict[str, Any]:
        """Set a parameter on a Fusion node.

        Args:
            node_name: Name of the node
            parameter: Parameter name to set
            value: Value to set for the parameter
        """
        try:
            validate_resolve_connection(resolve)
            validate_non_empty_string(node_name, "node_name")
            validate_non_empty_string(parameter, "parameter")
            
            comp = get_fusion_comp(resolve)
            
            # Find the node
            node = find_node(comp, node_name)
            if not node:
                return error(f"Node '{node_name}' not found", "NODE_NOT_FOUND")
            
            # Set the parameter
            success_set = set_node_input(node, parameter, value)
            if not success_set:
                return error(f"Failed to set parameter '{parameter}' on node '{node_name}'")
            
            return success(f"Set {parameter} = {value} on node '{node_name}'")
            
        except ValidationError as e:
            return error(str(e), "VALIDATION_ERROR")
        except Exception as e:
            return error(f"Error setting node parameter: {str(e)}")

    @mcp.resource("resolve://fusion/available-nodes")
    def get_available_fusion_nodes() -> Dict[str, Any]:
        """Get list of available Fusion node types."""
        return info("Available Fusion node types", get_node_categories())

    @mcp.tool()
    @ensure_page("fusion")
    def create_fusion_clip(timeline_item_name: str = None) -> Dict[str, Any]:
        """Create a new Fusion clip from a timeline item.

        Args:
            timeline_item_name: Name of the timeline item to convert to Fusion clip
        """
        try:
            validate_resolve_connection(resolve)
            
            project_manager = resolve.GetProjectManager()
            if not project_manager:
                return error("Failed to get Project Manager")

            current_project = project_manager.GetCurrentProject()
            if not current_project:
                return error("No project currently open")

            current_timeline = current_project.GetCurrentTimeline()
            if not current_timeline:
                return error("No timeline currently active")

            # Find the timeline item
            target_item = None
            if timeline_item_name:
                validate_non_empty_string(timeline_item_name, "timeline_item_name")
                # Search for specific item by name
                video_track_count = current_timeline.GetTrackCount("video")

                for track_index in range(1, video_track_count + 1):
                    items = current_timeline.GetItemListInTrack("video", track_index)
                    if items:
                        for item in items:
                            if item.GetName() == timeline_item_name:
                                target_item = item
                                break
                    if target_item:
                        break

                if not target_item:
                    return error(f"Timeline item '{timeline_item_name}' not found", "ITEM_NOT_FOUND")

                # Select the item
                current_timeline.SetCurrentVideoItem(target_item)
            else:
                target_item = current_timeline.GetCurrentVideoItem()
                if not target_item:
                    return error("No timeline item selected")

            # Create Fusion clip
            result = current_timeline.CreateFusionClip([target_item])

            if result:
                item_name = timeline_item_name or target_item.GetName()
                return success(f"Created Fusion clip from '{item_name}'")
            else:
                return error("Failed to create Fusion clip")

        except ValidationError as e:
            return error(str(e), "VALIDATION_ERROR")
        except Exception as e:
            return error(f"Error creating Fusion clip: {str(e)}")

    @mcp.tool()
    @ensure_page("fusion")
    def render_fusion_composition(start_frame: int = None, end_frame: int = None) -> Dict[str, Any]:
        """Render the current Fusion composition.

        Args:
            start_frame: Start frame for render (uses comp start if None)
            end_frame: End frame for render (uses comp end if None)
        """
        try:
            validate_resolve_connection(resolve)
            
            comp = get_fusion_comp(resolve)
            
            # Set render range if specified
            if start_frame is not None:
                comp.SetAttrs({"COMPN_RenderStart": start_frame})

            if end_frame is not None:
                comp.SetAttrs({"COMPN_RenderEnd": end_frame})

            # Start render
            comp.Render()

            render_start = comp.GetAttrs().get("COMPN_RenderStart", 0)
            render_end = comp.GetAttrs().get("COMPN_RenderEnd", 0)

            return success(f"Started rendering Fusion composition from frame {render_start} to {render_end}", {
                "render_start": render_start,
                "render_end": render_end
            })

        except ValidationError as e:
            return error(str(e), "VALIDATION_ERROR")
        except Exception as e:
            return error(f"Error rendering Fusion composition: {str(e)}")
