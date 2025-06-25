"""
Fusion Operations Module
Handles DaVinci Resolve Fusion page operations and detailed effects
Comprehensive visual effects and compositing capabilities
"""

from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger("davinci-resolve-mcp.fusion")

def register_fusion_operations(mcp, resolve: Optional[object]):
    """Register comprehensive Fusion page operations with the MCP server."""
    
    # ------------------
    # Core Node Operations
    # ------------------
    
    @mcp.resource("resolve://fusion/composition")
    def get_fusion_composition() -> Dict[str, Any]:
        """Get information about the current Fusion composition."""
        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve"}
        
        try:
            project_manager = resolve.GetProjectManager()
            if not project_manager:
                return {"error": "Failed to get Project Manager"}
            
            current_project = project_manager.GetCurrentProject()
            if not current_project:
                return {"error": "No project currently open"}
            
            current_timeline = current_project.GetCurrentTimeline()
            if not current_timeline:
                return {"error": "No timeline currently active"}
            
            # Switch to Fusion page
            current_page = resolve.GetCurrentPage()
            if current_page != "fusion":
                resolve.OpenPage("fusion")
            
            # Get Fusion composition info
            fusion = resolve.Fusion()
            if not fusion:
                return {"error": "Failed to access Fusion"}
            
            comp = fusion.GetCurrentComp()
            if not comp:
                return {"error": "No Fusion composition active"}
            
            comp_info = {
                "name": comp.GetAttrs().get("COMPN_Name", "Unknown"),
                "frame_format": comp.GetAttrs().get("COMPN_GlobalStart", 0),
                "duration": comp.GetAttrs().get("COMPN_GlobalEnd", 0) - comp.GetAttrs().get("COMPN_GlobalStart", 0),
                "current_time": comp.CurrentTime,
                "render_start": comp.GetAttrs().get("COMPN_RenderStart", 0),
                "render_end": comp.GetAttrs().get("COMPN_RenderEnd", 0),
                "fps": comp.GetAttrs().get("COMPN_FrameRate", 24.0),
                "resolution": {
                    "width": comp.GetAttrs().get("COMPN_ImageWidth", 1920),
                    "height": comp.GetAttrs().get("COMPN_ImageHeight", 1080),
                    "aspect": comp.GetAttrs().get("COMPN_ImageAspect", 1.0)
                }
            }
            
            return comp_info
            
        except Exception as e:
            return {"error": f"Error accessing Fusion composition: {str(e)}"}
    
    @mcp.resource("resolve://fusion/nodes")
    def get_fusion_nodes() -> List[Dict[str, Any]]:
        """Get all nodes in the current Fusion composition."""
        if resolve is None:
            return [{"error": "Not connected to DaVinci Resolve"}]
        
        try:
            fusion = resolve.Fusion()
            if not fusion:
                return [{"error": "Failed to access Fusion"}]
            
            comp = fusion.GetCurrentComp()
            if not comp:
                return [{"error": "No Fusion composition active"}]
            
            nodes = []
            tool_list = comp.GetToolList()
            
            for name, tool in tool_list.items():
                node_info = {
                    "name": name,
                    "type": tool.GetAttrs()["TOOLS_RegID"],
                    "id": tool.ID,
                    "pos_x": tool.GetAttrs().get("TOOLNT_Position_X", 0),
                    "pos_y": tool.GetAttrs().get("TOOLNT_Position_Y", 0),
                    "selected": tool.GetAttrs().get("TOOLB_Selected", False),
                    "locked": tool.GetAttrs().get("TOOLB_Locked", False),
                    "pass_through": tool.GetAttrs().get("TOOLB_PassThrough", False)
                }
                nodes.append(node_info)
            
            return nodes
            
        except Exception as e:
            return [{"error": f"Error getting Fusion nodes: {str(e)}"}]
    
    @mcp.tool()
    def add_fusion_node(node_type: str, name: str = None, pos_x: float = 0, pos_y: float = 0) -> str:
        """Add a new node to the Fusion composition.
        
        Args:
            node_type: Type of node to add (e.g., 'Transform', 'Merge', 'ColorCorrector')
            name: Optional custom name for the node
            pos_x: X position in the flow area
            pos_y: Y position in the flow area
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        try:
            # Switch to Fusion page
            current_page = resolve.GetCurrentPage()
            if current_page != "fusion":
                resolve.OpenPage("fusion")
            
            fusion = resolve.Fusion()
            if not fusion:
                return "Error: Failed to access Fusion"
            
            comp = fusion.GetCurrentComp()
            if not comp:
                return "Error: No Fusion composition active"
            
            # Add the node
            node = comp.AddTool(node_type)
            if not node:
                return f"Error: Failed to create node of type '{node_type}'"
            
            # Set custom name if provided
            if name:
                node.SetAttrs({"TOOLS_Name": name})
            
            # Set position
            if pos_x != 0 or pos_y != 0:
                node.SetAttrs({
                    "TOOLNT_Position_X": pos_x,
                    "TOOLNT_Position_Y": pos_y
                })
            
            node_name = node.GetAttrs()["TOOLS_Name"]
            return f"Successfully added {node_type} node: {node_name}"
            
        except Exception as e:
            return f"Error adding Fusion node: {str(e)}"
    
    @mcp.tool()
    def connect_fusion_nodes(output_node: str, input_node: str, input_name: str = "Input") -> str:
        """Connect two nodes in the Fusion composition.
        
        Args:
            output_node: Name of the source node
            input_node: Name of the destination node
            input_name: Name of the input on the destination node
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        try:
            fusion = resolve.Fusion()
            if not fusion:
                return "Error: Failed to access Fusion"
            
            comp = fusion.GetCurrentComp()
            if not comp:
                return "Error: No Fusion composition active"
            
            # Get the nodes
            output_tool = comp.FindTool(output_node)
            input_tool = comp.FindTool(input_node)
            
            if not output_tool:
                return f"Error: Output node '{output_node}' not found"
            
            if not input_tool:
                return f"Error: Input node '{input_node}' not found"
            
            # Connect the nodes
            input_tool.ConnectInput(input_name, output_tool)
            
            return f"Successfully connected {output_node} to {input_node}.{input_name}"
            
        except Exception as e:
            return f"Error connecting Fusion nodes: {str(e)}"
    
    @mcp.tool()
    def delete_fusion_node(node_name: str) -> str:
        """Delete a node from the Fusion composition.
        
        Args:
            node_name: Name of the node to delete
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        try:
            fusion = resolve.Fusion()
            if not fusion:
                return "Error: Failed to access Fusion"
            
            comp = fusion.GetCurrentComp()
            if not comp:
                return "Error: No Fusion composition active"
            
            # Find and delete the node
            node = comp.FindTool(node_name)
            if not node:
                return f"Error: Node '{node_name}' not found"
            
            node.Delete()
            return f"Successfully deleted node: {node_name}"
            
        except Exception as e:
            return f"Error deleting Fusion node: {str(e)}"
    
    # ------------------
    # Transform & Geometry
    # ------------------
    
    @mcp.tool()
    def add_transform_node(name: str = None, x: float = 0, y: float = 0, 
                          rotation: float = 0, size: float = 1.0) -> str:
        """Add a Transform node with specified parameters.
        
        Args:
            name: Optional custom name for the node
            x: X translation
            y: Y translation
            rotation: Rotation in degrees
            size: Scale factor
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        try:
            fusion = resolve.Fusion()
            comp = fusion.GetCurrentComp()
            
            transform = comp.AddTool("Transform")
            if name:
                transform.SetAttrs({"TOOLS_Name": name})
            
            # Set transform parameters
            transform.Center[1] = x
            transform.Center[2] = y
            transform.Angle[0] = rotation
            transform.Size[0] = size
            
            node_name = transform.GetAttrs()["TOOLS_Name"]
            return f"Successfully added Transform node: {node_name}"
            
        except Exception as e:
            return f"Error adding Transform node: {str(e)}"
    
    @mcp.tool()
    def add_corner_position_node(name: str = None) -> str:
        """Add a Corner Positioner node for 4-corner positioning.
        
        Args:
            name: Optional custom name for the node
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        try:
            fusion = resolve.Fusion()
            comp = fusion.GetCurrentComp()
            
            corner_pin = comp.AddTool("CornerPin")
            if name:
                corner_pin.SetAttrs({"TOOLS_Name": name})
            
            node_name = corner_pin.GetAttrs()["TOOLS_Name"]
            return f"Successfully added Corner Positioner node: {node_name}"
            
        except Exception as e:
            return f"Error adding Corner Positioner node: {str(e)}"
    
    # ------------------
    # Compositing & Blending
    # ------------------
    
    @mcp.tool()
    def add_merge_node(name: str = None, blend_mode: str = "Normal", 
                      opacity: float = 1.0) -> str:
        """Add a Merge node for compositing layers.
        
        Args:
            name: Optional custom name for the node
            blend_mode: Blend mode (Normal, Add, Multiply, Screen, etc.)
            opacity: Opacity value (0.0 to 1.0)
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        try:
            fusion = resolve.Fusion()
            comp = fusion.GetCurrentComp()
            
            merge = comp.AddTool("Merge")
            if name:
                merge.SetAttrs({"TOOLS_Name": name})
            
            # Set blend mode and opacity
            blend_modes = {
                "Normal": 0, "Add": 1, "Multiply": 2, "Screen": 3,
                "Overlay": 4, "SoftLight": 5, "HardLight": 6,
                "Darken": 7, "Lighten": 8, "Difference": 9
            }
            
            if blend_mode in blend_modes:
                merge.Operator[0] = blend_modes[blend_mode]
            
            merge.Blend[0] = opacity
            
            node_name = merge.GetAttrs()["TOOLS_Name"]
            return f"Successfully added Merge node: {node_name}"
            
        except Exception as e:
            return f"Error adding Merge node: {str(e)}"
    
    # ------------------
    # Keying & Masking
    # ------------------
    
    @mcp.tool()
    def add_chroma_keyer(name: str = None, key_color: str = "green") -> str:
        """Add a Chroma Keyer for green/blue screen keying.
        
        Args:
            name: Optional custom name for the node
            key_color: Color to key out (green, blue, or custom)
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        try:
            fusion = resolve.Fusion()
            comp = fusion.GetCurrentComp()
            
            chroma_key = comp.AddTool("ChromaKeyer")
            if name:
                chroma_key.SetAttrs({"TOOLS_Name": name})
            
            # Set key color presets
            if key_color.lower() == "green":
                chroma_key.MatteControl.KeyColor = {0.0, 1.0, 0.0, 1.0}
            elif key_color.lower() == "blue":
                chroma_key.MatteControl.KeyColor = {0.0, 0.0, 1.0, 1.0}
            
            node_name = chroma_key.GetAttrs()["TOOLS_Name"]
            return f"Successfully added Chroma Keyer node: {node_name}"
            
        except Exception as e:
            return f"Error adding Chroma Keyer node: {str(e)}"
    
    @mcp.tool()
    def add_polygon_mask(name: str = None) -> str:
        """Add a Polygon mask for vector-based masking.
        
        Args:
            name: Optional custom name for the node
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        try:
            fusion = resolve.Fusion()
            comp = fusion.GetCurrentComp()
            
            polygon = comp.AddTool("Polygon")
            if name:
                polygon.SetAttrs({"TOOLS_Name": name})
            
            node_name = polygon.GetAttrs()["TOOLS_Name"]
            return f"Successfully added Polygon mask node: {node_name}"
            
        except Exception as e:
            return f"Error adding Polygon mask node: {str(e)}"
    
    # ------------------
    # Color Correction
    # ------------------
    
    @mcp.tool()
    def add_color_corrector(name: str = None, 
                           lift: tuple = (0.0, 0.0, 0.0, 0.0),
                           gamma: tuple = (1.0, 1.0, 1.0, 1.0),
                           gain: tuple = (1.0, 1.0, 1.0, 1.0)) -> str:
        """Add a Color Corrector node with specified color adjustments.
        
        Args:
            name: Optional custom name for the node
            lift: Lift values (R, G, B, Master)
            gamma: Gamma values (R, G, B, Master)
            gain: Gain values (R, G, B, Master)
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        try:
            fusion = resolve.Fusion()
            comp = fusion.GetCurrentComp()
            
            color_corrector = comp.AddTool("ColorCorrector")
            if name:
                color_corrector.SetAttrs({"TOOLS_Name": name})
            
            # Set color correction values
            color_corrector.ColorRanges.Shadows.Lift = lift
            color_corrector.ColorRanges.Midtones.Gamma = gamma
            color_corrector.ColorRanges.Highlights.Gain = gain
            
            node_name = color_corrector.GetAttrs()["TOOLS_Name"]
            return f"Successfully added Color Corrector node: {node_name}"
            
        except Exception as e:
            return f"Error adding Color Corrector node: {str(e)}"
    
    # ------------------
    # Filters & Effects
    # ------------------
    
    @mcp.tool()
    def add_blur_effect(name: str = None, blur_type: str = "Gaussian", 
                       blur_size: float = 5.0) -> str:
        """Add a blur effect node.
        
        Args:
            name: Optional custom name for the node
            blur_type: Type of blur (Gaussian, Radial, Motion, etc.)
            blur_size: Blur amount
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        try:
            fusion = resolve.Fusion()
            comp = fusion.GetCurrentComp()
            
            # Map blur types to tool names
            blur_tools = {
                "Gaussian": "Blur",
                "Radial": "RadialBlur", 
                "Motion": "DirectionalBlur",
                "Defocus": "Defocus"
            }
            
            tool_name = blur_tools.get(blur_type, "Blur")
            blur_node = comp.AddTool(tool_name)
            
            if name:
                blur_node.SetAttrs({"TOOLS_Name": name})
            
            # Set blur size
            if hasattr(blur_node, 'Size'):
                blur_node.Size[0] = blur_size
            elif hasattr(blur_node, 'Blur'):
                blur_node.Blur[0] = blur_size
            
            node_name = blur_node.GetAttrs()["TOOLS_Name"]
            return f"Successfully added {blur_type} blur node: {node_name}"
            
        except Exception as e:
            return f"Error adding blur node: {str(e)}"
    
    # ------------------
    # Text & Titles
    # ------------------
    
    @mcp.tool()
    def add_text_node(name: str = None, text: str = "Sample Text", 
                     font: str = "Arial", size: float = 0.1) -> str:
        """Add a Text+ node for advanced text creation.
        
        Args:
            name: Optional custom name for the node
            text: Text content
            font: Font name
            size: Text size (0.0 to 1.0)
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        try:
            fusion = resolve.Fusion()
            comp = fusion.GetCurrentComp()
            
            text_node = comp.AddTool("TextPlus")
            if name:
                text_node.SetAttrs({"TOOLS_Name": name})
            
            # Set text properties
            text_node.StyledText[0] = text
            text_node.Font[0] = font
            text_node.Size[0] = size
            
            node_name = text_node.GetAttrs()["TOOLS_Name"]
            return f"Successfully added Text+ node: {node_name}"
            
        except Exception as e:
            return f"Error adding Text+ node: {str(e)}"
    
    # ------------------
    # 3D Workspace
    # ------------------
    
    @mcp.tool()
    def add_3d_scene(name: str = None) -> str:
        """Add a 3D scene for 3D compositing.
        
        Args:
            name: Optional custom name for the node
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        try:
            fusion = resolve.Fusion()
            comp = fusion.GetCurrentComp()
            
            renderer_3d = comp.AddTool("Renderer3D")
            if name:
                renderer_3d.SetAttrs({"TOOLS_Name": name})
            
            node_name = renderer_3d.GetAttrs()["TOOLS_Name"]
            return f"Successfully added 3D Renderer node: {node_name}"
            
        except Exception as e:
            return f"Error adding 3D Renderer node: {str(e)}"
    
    @mcp.tool()
    def add_3d_camera(name: str = None) -> str:
        """Add a 3D camera for virtual camera controls.
        
        Args:
            name: Optional custom name for the node
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        try:
            fusion = resolve.Fusion()
            comp = fusion.GetCurrentComp()
            
            camera_3d = comp.AddTool("Camera3D")
            if name:
                camera_3d.SetAttrs({"TOOLS_Name": name})
            
            node_name = camera_3d.GetAttrs()["TOOLS_Name"]
            return f"Successfully added 3D Camera node: {node_name}"
            
        except Exception as e:
            return f"Error adding 3D Camera node: {str(e)}"
    
    # ------------------
    # Particle Systems
    # ------------------
    
    @mcp.tool()
    def add_particle_emitter(name: str = None, emission_rate: float = 100.0) -> str:
        """Add a particle emitter for particle effects.
        
        Args:
            name: Optional custom name for the node
            emission_rate: Number of particles per frame
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        try:
            fusion = resolve.Fusion()
            comp = fusion.GetCurrentComp()
            
            emitter = comp.AddTool("pEmitter")
            if name:
                emitter.SetAttrs({"TOOLS_Name": name})
            
            # Set emission rate
            emitter.Number[0] = emission_rate
            
            node_name = emitter.GetAttrs()["TOOLS_Name"]
            return f"Successfully added Particle Emitter node: {node_name}"
            
        except Exception as e:
            return f"Error adding Particle Emitter node: {str(e)}"
    
    @mcp.tool()
    def add_particle_renderer(name: str = None) -> str:
        """Add a particle renderer to visualize particles.
        
        Args:
            name: Optional custom name for the node
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        try:
            fusion = resolve.Fusion()
            comp = fusion.GetCurrentComp()
            
            renderer = comp.AddTool("pRender")
            if name:
                renderer.SetAttrs({"TOOLS_Name": name})
            
            node_name = renderer.GetAttrs()["TOOLS_Name"]
            return f"Successfully added Particle Renderer node: {node_name}"
            
        except Exception as e:
            return f"Error adding Particle Renderer node: {str(e)}"
    
    # ------------------
    # Generators
    # ------------------
    
    @mcp.tool()
    def add_background_generator(name: str = None, color: tuple = (0.0, 0.0, 0.0, 1.0)) -> str:
        """Add a background generator for solid colors and gradients.
        
        Args:
            name: Optional custom name for the node
            color: RGBA color values (0.0 to 1.0)
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        try:
            fusion = resolve.Fusion()
            comp = fusion.GetCurrentComp()
            
            background = comp.AddTool("Background")
            if name:
                background.SetAttrs({"TOOLS_Name": name})
            
            # Set background color
            background.TopLeftColor = color
            
            node_name = background.GetAttrs()["TOOLS_Name"]
            return f"Successfully added Background generator node: {node_name}"
            
        except Exception as e:
            return f"Error adding Background generator node: {str(e)}"
    
    # ------------------
    # Time Effects
    # ------------------
    
    @mcp.tool()
    def add_time_speed_effect(name: str = None, speed: float = 1.0) -> str:
        """Add a time speed effect for speed ramping.
        
        Args:
            name: Optional custom name for the node
            speed: Speed multiplier (0.5 = half speed, 2.0 = double speed)
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        try:
            fusion = resolve.Fusion()
            comp = fusion.GetCurrentComp()
            
            time_speed = comp.AddTool("TimeSpeed")
            if name:
                time_speed.SetAttrs({"TOOLS_Name": name})
            
            # Set speed
            time_speed.Speed[0] = speed
            
            node_name = time_speed.GetAttrs()["TOOLS_Name"]
            return f"Successfully added Time Speed node: {node_name}"
            
        except Exception as e:
            return f"Error adding Time Speed node: {str(e)}"
    
    # ------------------
    # Macros & Tools
    # ------------------
    
    @mcp.tool()
    def create_macro(node_names: List[str], macro_name: str) -> str:
        """Group nodes into a reusable macro.
        
        Args:
            node_names: List of node names to include in the macro
            macro_name: Name for the new macro
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        try:
            fusion = resolve.Fusion()
            comp = fusion.GetCurrentComp()
            
            # Find all nodes to include
            nodes = []
            for node_name in node_names:
                node = comp.FindTool(node_name)
                if node:
                    nodes.append(node)
                else:
                    return f"Error: Node '{node_name}' not found"
            
            if not nodes:
                return "Error: No valid nodes found for macro creation"
            
            # Create macro (this is a simplified version)
            # In practice, you'd need to implement more complex macro creation logic
            macro = comp.CreateMacro(nodes, macro_name)
            
            return f"Successfully created macro: {macro_name}"
            
        except Exception as e:
            return f"Error creating macro: {str(e)}"
    
    # ------------------
    # Import/Export
    # ------------------
    
    @mcp.tool()
    def save_fusion_composition(file_path: str) -> str:
        """Save the current Fusion composition to a file.
        
        Args:
            file_path: Path to save the composition file
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        try:
            fusion = resolve.Fusion()
            comp = fusion.GetCurrentComp()
            
            if not comp:
                return "Error: No active composition to save"
            
            result = comp.Save(file_path)
            
            if result:
                return f"Successfully saved composition to: {file_path}"
            else:
                return f"Failed to save composition to: {file_path}"
            
        except Exception as e:
            return f"Error saving composition: {str(e)}"
    
    @mcp.tool()
    def load_fusion_composition(file_path: str) -> str:
        """Load a Fusion composition from a file.
        
        Args:
            file_path: Path to the composition file to load
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        try:
            fusion = resolve.Fusion()
            
            comp = fusion.LoadComp(file_path)
            
            if comp:
                return f"Successfully loaded composition from: {file_path}"
            else:
                return f"Failed to load composition from: {file_path}"
            
        except Exception as e:
            return f"Error loading composition: {str(e)}"
                "locked": comp.GetAttrs().get("COMPN_Locked", False)
            }
            
            # Return to original page
            if current_page != "fusion":
                resolve.OpenPage(current_page)
            
            return comp_info
            
        except Exception as e:
            return {"error": f"Error getting Fusion composition info: {str(e)}"}

    @mcp.tool()
    def create_fusion_clip(timeline_item_name: str = None) -> str:
        """Create a new Fusion clip from a timeline item.
        
        Args:
            timeline_item_name: Name of the timeline item to convert to Fusion clip
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        try:
            project_manager = resolve.GetProjectManager()
            if not project_manager:
                return "Error: Failed to get Project Manager"
            
            current_project = project_manager.GetCurrentProject()
            if not current_project:
                return "Error: No project currently open"
            
            current_timeline = current_project.GetCurrentTimeline()
            if not current_timeline:
                return "Error: No timeline currently active"
            
            # Find the timeline item
            if timeline_item_name:
                # Search for specific item by name
                video_track_count = current_timeline.GetTrackCount("video")
                target_item = None
                
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
                    return f"Error: Timeline item '{timeline_item_name}' not found"
                
                # Select the item
                current_timeline.SetCurrentVideoItem(target_item)
            
            # Create Fusion clip
            result = current_timeline.CreateFusionClip([current_timeline.GetCurrentVideoItem()])
            
            if result:
                return f"Successfully created Fusion clip from {timeline_item_name or 'current item'}"
            else:
                return f"Failed to create Fusion clip from {timeline_item_name or 'current item'}"
                
        except Exception as e:
            return f"Error creating Fusion clip: {str(e)}"

    @mcp.tool()
    def add_fusion_node(node_type: str, node_name: str = None) -> str:
        """Add a node to the current Fusion composition.
        
        Args:
            node_type: Type of node to add (e.g., 'Transform', 'Merge', 'Background', 'Text+')
            node_name: Optional custom name for the node
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        try:
            # Switch to Fusion page
            current_page = resolve.GetCurrentPage()
            if current_page != "fusion":
                resolve.OpenPage("fusion")
            
            fusion = resolve.Fusion()
            if not fusion:
                return "Error: Failed to access Fusion"
            
            comp = fusion.GetCurrentComp()
            if not comp:
                return "Error: No Fusion composition active"
            
            # Add the node
            node = comp.AddTool(node_type)
            if not node:
                return f"Error: Failed to add {node_type} node. Check if node type is valid."
            
            # Set custom name if provided
            if node_name:
                node.SetAttrs({"TOOLS_Name": node_name})
                actual_name = node_name
            else:
                actual_name = node.GetAttrs().get("TOOLS_Name", node_type)
            
            # Return to original page
            if current_page != "fusion":
                resolve.OpenPage(current_page)
            
            return f"Successfully added {node_type} node '{actual_name}'"
            
        except Exception as e:
            if current_page != "fusion":
                resolve.OpenPage(current_page)
            return f"Error adding Fusion node: {str(e)}"

    @mcp.tool()
    def connect_fusion_nodes(source_node: str, target_node: str, 
                           source_output: str = "Output", target_input: str = "Foreground") -> str:
        """Connect two nodes in the Fusion composition.
        
        Args:
            source_node: Name of the source node
            target_node: Name of the target node
            source_output: Output connector name (default: "Output")
            target_input: Input connector name (default: "Foreground")
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        try:
            # Switch to Fusion page
            current_page = resolve.GetCurrentPage()
            if current_page != "fusion":
                resolve.OpenPage("fusion")
            
            fusion = resolve.Fusion()
            if not fusion:
                return "Error: Failed to access Fusion"
            
            comp = fusion.GetCurrentComp()
            if not comp:
                return "Error: No Fusion composition active"
            
            # Find the nodes
            source = comp.FindTool(source_node)
            target = comp.FindTool(target_node)
            
            if not source:
                return f"Error: Source node '{source_node}' not found"
            
            if not target:
                return f"Error: Target node '{target_node}' not found"
            
            # Connect the nodes
            target_input_obj = target.FindMainInput(target_input)
            source_output_obj = source.FindMainOutput(source_output)
            
            if not target_input_obj:
                return f"Error: Input '{target_input}' not found on target node"
            
            if not source_output_obj:
                return f"Error: Output '{source_output}' not found on source node"
            
            target_input_obj.ConnectTo(source_output_obj)
            
            # Return to original page
            if current_page != "fusion":
                resolve.OpenPage(current_page)
            
            return f"Successfully connected {source_node}.{source_output} to {target_node}.{target_input}"
            
        except Exception as e:
            if current_page != "fusion":
                resolve.OpenPage(current_page)
            return f"Error connecting Fusion nodes: {str(e)}"

    @mcp.tool()
    def set_fusion_node_parameter(node_name: str, parameter: str, value: Any) -> str:
        """Set a parameter on a Fusion node.
        
        Args:
            node_name: Name of the node
            parameter: Parameter name to set
            value: Value to set for the parameter
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        try:
            # Switch to Fusion page
            current_page = resolve.GetCurrentPage()
            if current_page != "fusion":
                resolve.OpenPage("fusion")
            
            fusion = resolve.Fusion()
            if not fusion:
                return "Error: Failed to access Fusion"
            
            comp = fusion.GetCurrentComp()
            if not comp:
                return "Error: No Fusion composition active"
            
            # Find the node
            node = comp.FindTool(node_name)
            if not node:
                return f"Error: Node '{node_name}' not found"
            
            # Set the parameter
            input_obj = node.FindMainInput(parameter)
            if input_obj:
                input_obj.SetAttrs({"INPB_Source": value})
            else:
                # Try setting as attribute
                node.SetAttrs({parameter: value})
            
            # Return to original page
            if current_page != "fusion":
                resolve.OpenPage(current_page)
            
            return f"Successfully set {parameter} = {value} on node '{node_name}'"
            
        except Exception as e:
            if current_page != "fusion":
                resolve.OpenPage(current_page)
            return f"Error setting Fusion node parameter: {str(e)}"

    @mcp.tool()
    def create_fusion_text(text_content: str, node_name: str = None) -> str:
        """Create a Text+ node with specified content.
        
        Args:
            text_content: The text content to display
            node_name: Optional custom name for the text node
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        try:
            # Switch to Fusion page
            current_page = resolve.GetCurrentPage()
            if current_page != "fusion":
                resolve.OpenPage("fusion")
            
            fusion = resolve.Fusion()
            if not fusion:
                return "Error: Failed to access Fusion"
            
            comp = fusion.GetCurrentComp()
            if not comp:
                return "Error: No Fusion composition active"
            
            # Create Text+ node
            text_node = comp.AddTool("TextPlus")
            if not text_node:
                return "Error: Failed to create Text+ node"
            
            # Set text content
            text_input = text_node.FindMainInput("StyledText")
            if text_input:
                text_input.SetAttrs({"INPB_Source": text_content})
            
            # Set custom name if provided
            if node_name:
                text_node.SetAttrs({"TOOLS_Name": node_name})
                actual_name = node_name
            else:
                actual_name = text_node.GetAttrs().get("TOOLS_Name", "Text+")
            
            # Return to original page
            if current_page != "fusion":
                resolve.OpenPage(current_page)
            
            return f"Successfully created Text+ node '{actual_name}' with content: '{text_content}'"
            
        except Exception as e:
            if current_page != "fusion":
                resolve.OpenPage(current_page)
            return f"Error creating Fusion text: {str(e)}"

    @mcp.tool()
    def create_fusion_transform(node_name: str = None, 
                               center_x: float = 0.5, center_y: float = 0.5,
                               size: float = 1.0, angle: float = 0.0) -> str:
        """Create a Transform node with specified parameters.
        
        Args:
            node_name: Optional custom name for the transform node
            center_x: X position (0.0 to 1.0)
            center_y: Y position (0.0 to 1.0)  
            size: Scale factor (1.0 = 100%)
            angle: Rotation angle in degrees
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        try:
            # Switch to Fusion page
            current_page = resolve.GetCurrentPage()
            if current_page != "fusion":
                resolve.OpenPage("fusion")
            
            fusion = resolve.Fusion()
            if not fusion:
                return "Error: Failed to access Fusion"
            
            comp = fusion.GetCurrentComp()
            if not comp:
                return "Error: No Fusion composition active"
            
            # Create Transform node
            transform_node = comp.AddTool("Transform")
            if not transform_node:
                return "Error: Failed to create Transform node"
            
            # Set transform parameters
            center_input = transform_node.FindMainInput("Center")
            if center_input:
                center_input.SetAttrs({"INPB_Source": [center_x, center_y]})
            
            size_input = transform_node.FindMainInput("Size")
            if size_input:
                size_input.SetAttrs({"INPB_Source": size})
            
            angle_input = transform_node.FindMainInput("Angle")
            if angle_input:
                angle_input.SetAttrs({"INPB_Source": angle})
            
            # Set custom name if provided
            if node_name:
                transform_node.SetAttrs({"TOOLS_Name": node_name})
                actual_name = node_name
            else:
                actual_name = transform_node.GetAttrs().get("TOOLS_Name", "Transform")
            
            # Return to original page
            if current_page != "fusion":
                resolve.OpenPage(current_page)
            
            return f"Successfully created Transform node '{actual_name}' with center=({center_x}, {center_y}), size={size}, angle={angle}°"
            
        except Exception as e:
            if current_page != "fusion":
                resolve.OpenPage(current_page)
            return f"Error creating Fusion transform: {str(e)}"

    @mcp.resource("resolve://fusion/available-nodes")
    def get_available_fusion_nodes() -> Dict[str, Any]:
        """Get list of available Fusion node types."""
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
                "Transform", "DVE", "Corner Pin", "Grid Warp", "Lens Distortion",
                "Perspective", "Resize", "Crop"
            ],
            "filters": [
                "Blur", "Sharpen", "Glow", "Soft Glow", "Unsharp Mask",
                "Despill", "Emboss", "Sobel", "Erode", "Dilate"
            ],
            "keying": [
                "Chroma Keyer", "Luma Keyer", "Color Keyer", "Delta Keyer",
                "Primatte", "Ultra Keyer"
            ],
            "3d": [
                "3D", "Camera3D", "ImagePlane3D", "Merge3D", "Renderer3D",
                "Shape3D", "Spotlight3D", "Transform3D"
            ],
            "particles": [
                "pEmitter", "pRender", "pBounce", "pDirectionalForce",
                "pGravity", "pKill", "pSpawn", "pTurbulence"
            ],
            "tracking": [
                "Tracker", "PlanarTracker", "CameraTracker", "Stabilizer"
            ],
            "effects": [
                "DisplacementMap", "Distortion", "Ripple", "Spherical",
                "Tile", "TimeSpeed", "Trails", "Echo"
            ]
        }

    @mcp.tool()
    def render_fusion_composition(start_frame: int = None, end_frame: int = None,
                                output_path: str = None) -> str:
        """Render the current Fusion composition.
        
        Args:
            start_frame: Start frame for render (uses comp start if None)
            end_frame: End frame for render (uses comp end if None)
            output_path: Output file path (uses default if None)
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        try:
            # Switch to Fusion page
            current_page = resolve.GetCurrentPage()
            if current_page != "fusion":
                resolve.OpenPage("fusion")
            
            fusion = resolve.Fusion()
            if not fusion:
                return "Error: Failed to access Fusion"
            
            comp = fusion.GetCurrentComp()
            if not comp:
                return "Error: No Fusion composition active"
            
            # Set render range
            if start_frame is not None:
                comp.SetAttrs({"COMPN_RenderStart": start_frame})
            
            if end_frame is not None:
                comp.SetAttrs({"COMPN_RenderEnd": end_frame})
            
            # Start render
            comp.Render()
            
            render_start = comp.GetAttrs().get("COMPN_RenderStart", 0)
            render_end = comp.GetAttrs().get("COMPN_RenderEnd", 0)
            
            # Return to original page
            if current_page != "fusion":
                resolve.OpenPage(current_page)
            
            return f"Started rendering Fusion composition from frame {render_start} to {render_end}"
            
        except Exception as e:
            if current_page != "fusion":
                resolve.OpenPage(current_page)
            return f"Error rendering Fusion composition: {str(e)}"
