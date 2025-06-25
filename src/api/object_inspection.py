"""
Object Inspection Module
Handles DaVinci Resolve API object inspection and introspection
"""

from typing import Optional, Dict, Any, List

def register_inspection_operations(mcp, resolve: Optional[object]):
    """Register object inspection operations with the MCP server."""
    
    @mcp.resource("resolve://inspect/resolve")
    def inspect_resolve_object() -> Dict[str, Any]:
        """Inspect the main Resolve object and its methods."""
        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve"}
        
        try:
            from src.utils.object_inspection import inspect_object
            return inspect_object(resolve, "Resolve")
        except Exception as e:
            return {"error": f"Error inspecting Resolve object: {str(e)}"}

    @mcp.resource("resolve://inspect/project-manager")
    def inspect_project_manager() -> Dict[str, Any]:
        """Inspect the ProjectManager object and its methods."""
        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve"}
        
        try:
            project_manager = resolve.GetProjectManager()
            if not project_manager:
                return {"error": "Failed to get Project Manager"}
            
            from src.utils.object_inspection import inspect_object
            return inspect_object(project_manager, "ProjectManager")
        except Exception as e:
            return {"error": f"Error inspecting ProjectManager: {str(e)}"}

    @mcp.resource("resolve://inspect/current-project")
    def inspect_current_project() -> Dict[str, Any]:
        """Inspect the current Project object and its methods."""
        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve"}
        
        try:
            project_manager = resolve.GetProjectManager()
            if not project_manager:
                return {"error": "Failed to get Project Manager"}
            
            current_project = project_manager.GetCurrentProject()
            if not current_project:
                return {"error": "No project currently open"}
            
            from src.utils.object_inspection import inspect_object
            return inspect_object(current_project, "Project")
        except Exception as e:
            return {"error": f"Error inspecting current project: {str(e)}"}

    @mcp.resource("resolve://inspect/media-pool")
    def inspect_media_pool() -> Dict[str, Any]:
        """Inspect the MediaPool object and its methods."""
        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve"}
        
        try:
            project_manager = resolve.GetProjectManager()
            if not project_manager:
                return {"error": "Failed to get Project Manager"}
            
            current_project = project_manager.GetCurrentProject()
            if not current_project:
                return {"error": "No project currently open"}
            
            media_pool = current_project.GetMediaPool()
            if not media_pool:
                return {"error": "Failed to get Media Pool"}
            
            from src.utils.object_inspection import inspect_object
            return inspect_object(media_pool, "MediaPool")
        except Exception as e:
            return {"error": f"Error inspecting MediaPool: {str(e)}"}

    @mcp.resource("resolve://inspect/current-timeline")
    def inspect_current_timeline() -> Dict[str, Any]:
        """Inspect the current Timeline object and its methods."""
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
            
            from src.utils.object_inspection import inspect_object
            return inspect_object(current_timeline, "Timeline")
        except Exception as e:
            return {"error": f"Error inspecting current timeline: {str(e)}"}

    @mcp.tool()
    def inspect_custom_object(object_path: str) -> str:
        """Inspect a custom object by following a path of method calls.
        
        Args:
            object_path: Dot-separated path to the object (e.g., "GetProjectManager.GetCurrentProject")
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        try:
            # Start with the resolve object
            current_obj = resolve
            path_parts = object_path.split('.')
            
            # Follow the path
            for part in path_parts:
                if hasattr(current_obj, part):
                    method = getattr(current_obj, part)
                    if callable(method):
                        current_obj = method()
                    else:
                        current_obj = method
                else:
                    return f"Error: '{part}' not found in object path"
            
            if current_obj is None:
                return f"Error: Object path '{object_path}' returned None"
            
            # Inspect the final object
            from src.utils.object_inspection import inspect_object
            result = inspect_object(current_obj, object_path)
            
            # Convert to string for tool return
            import json
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error inspecting object at path '{object_path}': {str(e)}"

    @mcp.tool()
    def get_object_methods(object_path: str = "resolve") -> str:
        """Get all methods available on a DaVinci Resolve object.
        
        Args:
            object_path: Path to the object (default: "resolve" for main object)
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        try:
            # Get the object
            if object_path == "resolve":
                target_obj = resolve
            else:
                # Follow the path
                current_obj = resolve
                path_parts = object_path.split('.')
                
                for part in path_parts:
                    if hasattr(current_obj, part):
                        method = getattr(current_obj, part)
                        if callable(method):
                            current_obj = method()
                        else:
                            current_obj = method
                    else:
                        return f"Error: '{part}' not found in object path"
                
                target_obj = current_obj
            
            if target_obj is None:
                return f"Error: Object path '{object_path}' returned None"
            
            # Get methods
            from src.utils.object_inspection import get_object_methods
            methods = get_object_methods(target_obj)
            
            # Format as string
            method_list = "\n".join([f"- {method}" for method in sorted(methods)])
            return f"Methods available on {object_path}:\n{method_list}"
            
        except Exception as e:
            return f"Error getting methods for '{object_path}': {str(e)}"

    @mcp.tool()
    def get_object_properties(object_path: str = "resolve") -> str:
        """Get all properties available on a DaVinci Resolve object.
        
        Args:
            object_path: Path to the object (default: "resolve" for main object)
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        try:
            # Get the object
            if object_path == "resolve":
                target_obj = resolve
            else:
                # Follow the path
                current_obj = resolve
                path_parts = object_path.split('.')
                
                for part in path_parts:
                    if hasattr(current_obj, part):
                        method = getattr(current_obj, part)
                        if callable(method):
                            current_obj = method()
                        else:
                            current_obj = method
                    else:
                        return f"Error: '{part}' not found in object path"
                
                target_obj = current_obj
            
            if target_obj is None:
                return f"Error: Object path '{object_path}' returned None"
            
            # Get properties
            from src.utils.object_inspection import get_object_properties
            properties = get_object_properties(target_obj)
            
            # Format as string
            if properties:
                prop_list = "\n".join([f"- {prop}: {str(value)[:100]}" for prop, value in properties.items()])
                return f"Properties available on {object_path}:\n{prop_list}"
            else:
                return f"No properties found on {object_path}"
            
        except Exception as e:
            return f"Error getting properties for '{object_path}': {str(e)}"

    @mcp.tool()
    def test_object_method(object_path: str, method_name: str, *args) -> str:
        """Test calling a method on a DaVinci Resolve object.
        
        Args:
            object_path: Path to the object
            method_name: Name of the method to call
            *args: Arguments to pass to the method
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        try:
            # Get the object
            if object_path == "resolve":
                target_obj = resolve
            else:
                # Follow the path
                current_obj = resolve
                path_parts = object_path.split('.')
                
                for part in path_parts:
                    if hasattr(current_obj, part):
                        method = getattr(current_obj, part)
                        if callable(method):
                            current_obj = method()
                        else:
                            current_obj = method
                    else:
                        return f"Error: '{part}' not found in object path"
                
                target_obj = current_obj
            
            if target_obj is None:
                return f"Error: Object path '{object_path}' returned None"
            
            # Check if method exists
            if not hasattr(target_obj, method_name):
                return f"Error: Method '{method_name}' not found on {object_path}"
            
            method = getattr(target_obj, method_name)
            if not callable(method):
                return f"Error: '{method_name}' is not a callable method"
            
            # Call the method
            if args:
                result = method(*args)
            else:
                result = method()
            
            return f"Method {object_path}.{method_name}({', '.join(map(str, args))}) returned: {result}"
            
        except Exception as e:
            return f"Error calling method {method_name} on {object_path}: {str(e)}"

    @mcp.resource("resolve://api/documentation")
    def get_api_documentation() -> Dict[str, Any]:
        """Get comprehensive API documentation for DaVinci Resolve objects."""
        return {
            "main_objects": {
                "Resolve": {
                    "description": "Main Resolve application object",
                    "key_methods": [
                        "GetProjectManager()", "GetCurrentPage()", "OpenPage(page)",
                        "GetProductName()", "GetVersionString()", "Quit()"
                    ]
                },
                "ProjectManager": {
                    "description": "Manages projects and databases",
                    "key_methods": [
                        "GetCurrentProject()", "CreateProject(name)", "LoadProject(name)",
                        "SaveProject()", "CloseProject(project)", "GetProjectListInCurrentFolder()"
                    ]
                },
                "Project": {
                    "description": "Represents a single project",
                    "key_methods": [
                        "GetMediaPool()", "GetCurrentTimeline()", "GetTimelineByIndex(idx)",
                        "SetCurrentTimeline(timeline)", "GetName()", "SetName(name)"
                    ]
                },
                "MediaPool": {
                    "description": "Manages media clips and folders",
                    "key_methods": [
                        "GetRootFolder()", "AddSubFolder(folder, name)", "ImportMedia(items)",
                        "CreateEmptyTimeline(name)", "AppendToTimeline(clips)"
                    ]
                },
                "Timeline": {
                    "description": "Represents a timeline/sequence",
                    "key_methods": [
                        "GetName()", "GetStartFrame()", "GetEndFrame()", "GetTrackCount(type)",
                        "GetItemListInTrack(type, index)", "AddMarker(frame, color, name, note)"
                    ]
                }
            },
            "common_workflows": [
                "Open project → Get media pool → Import media → Create timeline → Add clips",
                "Get timeline → Get clips → Modify properties → Add keyframes",
                "Switch to color page → Apply corrections → Save grades",
                "Add to render queue → Set format → Start rendering"
            ],
            "tips": [
                "Always check if objects are not None before using them",
                "Page switching may be required for certain operations",
                "Some operations require specific project states",
                "Use object inspection tools to discover available methods"
            ]
        }

    @mcp.tool()
    def generate_api_usage_example(operation: str) -> str:
        """Generate code examples for common DaVinci Resolve API operations.
        
        Args:
            operation: Type of operation (e.g., 'import_media', 'create_timeline', 'add_marker')
        """
        examples = {
            "import_media": '''
# Import media files into the media pool
project_manager = resolve.GetProjectManager()
project = project_manager.GetCurrentProject()
media_pool = project.GetMediaPool()

# Import files
file_paths = ["/path/to/video1.mp4", "/path/to/video2.mp4"]
clips = media_pool.ImportMedia(file_paths)

if clips:
    print(f"Successfully imported {len(clips)} clips")
else:
    print("Failed to import media")
            ''',
            "create_timeline": '''
# Create a new timeline
project_manager = resolve.GetProjectManager()
project = project_manager.GetCurrentProject()
media_pool = project.GetMediaPool()

# Create timeline
timeline = media_pool.CreateEmptyTimeline("My Timeline")

if timeline:
    print(f"Created timeline: {timeline.GetName()}")
    # Set as current timeline
    project.SetCurrentTimeline(timeline)
else:
    print("Failed to create timeline")
            ''',
            "add_marker": '''
# Add a marker to the timeline
project_manager = resolve.GetProjectManager()
project = project_manager.GetCurrentProject()
timeline = project.GetCurrentTimeline()

if timeline:
    # Add marker at frame 100
    result = timeline.AddMarker(100, "Red", "Scene 1", "Important scene")
    if result:
        print("Marker added successfully")
    else:
        print("Failed to add marker")
            ''',
            "switch_page": '''
# Switch between different pages in Resolve
current_page = resolve.GetCurrentPage()
print(f"Current page: {current_page}")

# Switch to color page
result = resolve.OpenPage("color")
if result:
    print("Switched to color page")
    
    # Do color operations here
    
    # Switch back to original page
    resolve.OpenPage(current_page)
            '''
        }
        
        if operation in examples:
            return f"Example for {operation}:\n{examples[operation]}"
        else:
            available_ops = ', '.join(examples.keys())
            return f"No example available for '{operation}'. Available examples: {available_ops}"
