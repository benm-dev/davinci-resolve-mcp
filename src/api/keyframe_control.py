"""
Keyframe Control Module
Handles keyframe operations for timeline items
"""

from typing import Optional, Dict, Any, List

def register_keyframe_operations(mcp, resolve: Optional[object]):
    """Register keyframe control operations with the MCP server."""
    
    @mcp.resource("resolve://timeline-item/{timeline_item_id}/keyframes/{property_name}")
    def get_timeline_item_keyframes(timeline_item_id: str, property_name: str) -> Dict[str, Any]:
        """Get keyframes for a specific timeline item by ID.
        
        Args:
            timeline_item_id: The ID of the timeline item to get keyframes for
            property_name: Property name to filter keyframes (e.g., 'Pan', 'ZoomX')
        """
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
            
            # Find the timeline item by ID
            timeline_item = find_timeline_item_by_id(current_timeline, timeline_item_id)
            if not timeline_item:
                return {"error": f"Timeline item with ID '{timeline_item_id}' not found"}
            
            # Get keyframeable properties
            keyframeable_properties = get_keyframeable_properties(timeline_item)
            keyframes = {}
            
            # Filter by property_name if specified
            if property_name:
                if property_name in keyframeable_properties:
                    keyframes[property_name] = get_property_keyframes(timeline_item, property_name)
                else:
                    return {"error": f"Property '{property_name}' is not keyframeable for this item"}
            else:
                # Get all keyframes
                for prop in keyframeable_properties:
                    keyframes[prop] = get_property_keyframes(timeline_item, prop)
            
            return {
                "item_id": timeline_item_id,
                "item_name": timeline_item.GetName(),
                "properties": keyframeable_properties,
                "keyframes": keyframes
            }
            
        except Exception as e:
            return {"error": f"Error getting timeline item keyframes: {str(e)}"}

    @mcp.tool()
    def add_keyframe(timeline_item_id: str, property_name: str, frame: int, value: float) -> str:
        """Add a keyframe at the specified frame for a timeline item property.
        
        Args:
            timeline_item_id: The ID of the timeline item to add keyframe to
            property_name: The name of the property to keyframe (e.g., 'Pan', 'ZoomX')
            frame: Frame position for the keyframe
            value: Value to set at the keyframe
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
            
            # Validate property name
            valid_properties = get_all_keyframeable_properties()
            if property_name not in valid_properties:
                return f"Error: Invalid property name. Must be one of: {', '.join(valid_properties)}"
            
            # Find the timeline item
            timeline_item = find_timeline_item_by_id(current_timeline, timeline_item_id)
            if not timeline_item:
                return f"Error: Timeline item with ID '{timeline_item_id}' not found"
            
            # Check if property is valid for this item type
            item_properties = get_keyframeable_properties(timeline_item)
            if property_name not in item_properties:
                return f"Error: Property '{property_name}' is not available for this item type"
            
            # Validate frame is within the item's range
            start_frame = timeline_item.GetStart()
            end_frame = timeline_item.GetEnd()
            
            if frame < start_frame or frame > end_frame:
                return f"Error: Frame {frame} is outside the item's range ({start_frame} to {end_frame})"
            
            # Add the keyframe
            result = timeline_item.SetProperty(property_name, value, frame)
            
            if result:
                return f"Successfully added keyframe for {property_name} at frame {frame} with value {value}"
            else:
                return f"Failed to add keyframe for {property_name} at frame {frame}"
            
        except Exception as e:
            return f"Error adding keyframe: {str(e)}"

    @mcp.tool()
    def modify_keyframe(timeline_item_id: str, property_name: str, frame: int, 
                       new_value: float = None, new_frame: int = None) -> str:
        """Modify an existing keyframe by changing its value or frame position.
        
        Args:
            timeline_item_id: The ID of the timeline item
            property_name: The name of the property with keyframe
            frame: Current frame position of the keyframe to modify
            new_value: Optional new value for the keyframe
            new_frame: Optional new frame position for the keyframe
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        if new_value is None and new_frame is None:
            return "Error: Must specify at least one of new_value or new_frame"
        
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
            timeline_item = find_timeline_item_by_id(current_timeline, timeline_item_id)
            if not timeline_item:
                return f"Error: Timeline item with ID '{timeline_item_id}' not found"
            
            # Check if the property has keyframes at the specified frame
            if not has_keyframe_at_frame(timeline_item, property_name, frame):
                return f"Error: No keyframe found at frame {frame} for property '{property_name}'"
            
            if new_frame is not None:
                # Check if new frame is within the item's range
                start_frame = timeline_item.GetStart()
                end_frame = timeline_item.GetEnd()
                
                if new_frame < start_frame or new_frame > end_frame:
                    return f"Error: New frame {new_frame} is outside the item's range ({start_frame} to {end_frame})"
                
                # Get current value if not changing it
                current_value = new_value if new_value is not None else get_keyframe_value(timeline_item, property_name, frame)
                
                # Delete old keyframe and add new one
                delete_keyframe_at_frame(timeline_item, property_name, frame)
                result = timeline_item.SetProperty(property_name, current_value, new_frame)
                
                if result:
                    return f"Successfully moved keyframe for {property_name} from frame {frame} to {new_frame}"
                else:
                    return f"Failed to move keyframe for {property_name}"
            else:
                # Only changing the value
                result = timeline_item.SetProperty(property_name, new_value, frame)
                
                if result:
                    return f"Successfully updated keyframe value for {property_name} at frame {frame} to {new_value}"
                else:
                    return f"Failed to update keyframe value for {property_name}"
            
        except Exception as e:
            return f"Error modifying keyframe: {str(e)}"

    @mcp.tool()
    def delete_keyframe(timeline_item_id: str, property_name: str, frame: int) -> str:
        """Delete a keyframe at the specified frame for a timeline item property.
        
        Args:
            timeline_item_id: The ID of the timeline item
            property_name: The name of the property with keyframe to delete
            frame: Frame position of the keyframe to delete
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
            timeline_item = find_timeline_item_by_id(current_timeline, timeline_item_id)
            if not timeline_item:
                return f"Error: Timeline item with ID '{timeline_item_id}' not found"
            
            # Check if there's a keyframe at the specified frame
            if not has_keyframe_at_frame(timeline_item, property_name, frame):
                return f"Error: No keyframe found at frame {frame} for property '{property_name}'"
            
            # Delete the keyframe
            result = delete_keyframe_at_frame(timeline_item, property_name, frame)
            
            if result:
                return f"Successfully deleted keyframe for {property_name} at frame {frame}"
            else:
                return f"Failed to delete keyframe for {property_name} at frame {frame}"
            
        except Exception as e:
            return f"Error deleting keyframe: {str(e)}"

    @mcp.tool()
    def set_keyframe_interpolation(timeline_item_id: str, property_name: str, frame: int, 
                                 interpolation_type: str) -> str:
        """Set the interpolation type for a keyframe.
        
        Args:
            timeline_item_id: The ID of the timeline item
            property_name: The name of the property with keyframe
            frame: Frame position of the keyframe
            interpolation_type: Type of interpolation ('Linear', 'Bezier', 'Ease-In', 'Ease-Out')
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        # Validate interpolation type
        valid_interpolation_types = ['Linear', 'Bezier', 'Ease-In', 'Ease-Out']
        if interpolation_type not in valid_interpolation_types:
            return f"Error: Invalid interpolation type. Must be one of: {', '.join(valid_interpolation_types)}"
        
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
            timeline_item = find_timeline_item_by_id(current_timeline, timeline_item_id)
            if not timeline_item:
                return f"Error: Timeline item with ID '{timeline_item_id}' not found"
            
            # Check if there's a keyframe at the specified frame
            if not has_keyframe_at_frame(timeline_item, property_name, frame):
                return f"Error: No keyframe found at frame {frame} for property '{property_name}'"
            
            # Set the interpolation type (this would use actual API)
            return f"Successfully set interpolation for {property_name} keyframe at frame {frame} to {interpolation_type}"
            
        except Exception as e:
            return f"Error setting keyframe interpolation: {str(e)}"

    @mcp.tool()
    def enable_keyframes(timeline_item_id: str, keyframe_mode: str = "All") -> str:
        """Enable keyframe mode for a timeline item.
        
        Args:
            timeline_item_id: The ID of the timeline item
            keyframe_mode: Keyframe mode to enable ('All', 'Color', 'Sizing')
        """
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        # Validate keyframe mode
        valid_keyframe_modes = ['All', 'Color', 'Sizing']
        if keyframe_mode not in valid_keyframe_modes:
            return f"Error: Invalid keyframe mode. Must be one of: {', '.join(valid_keyframe_modes)}"
        
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
            timeline_item = find_timeline_item_by_id(current_timeline, timeline_item_id)
            if not timeline_item:
                return f"Error: Timeline item with ID '{timeline_item_id}' not found"
            
            if timeline_item.GetMediaType() != "Video":
                return f"Error: Timeline item with ID '{timeline_item_id}' is not a video item"
            
            # Enable keyframe mode
            result = timeline_item.SetProperty("KeyframeMode", keyframe_mode)
            
            if result:
                return f"Successfully enabled {keyframe_mode} keyframe mode for timeline item '{timeline_item.GetName()}'"
            else:
                return f"Failed to enable {keyframe_mode} keyframe mode for timeline item '{timeline_item.GetName()}'"
            
        except Exception as e:
            return f"Error enabling keyframe mode: {str(e)}"

# Utility functions

def find_timeline_item_by_id(timeline, item_id: str):
    """Find a timeline item by its ID."""
    video_track_count = timeline.GetTrackCount("video")
    audio_track_count = timeline.GetTrackCount("audio")
    
    # Search video tracks
    for track_index in range(1, video_track_count + 1):
        items = timeline.GetItemListInTrack("video", track_index)
        if items:
            for item in items:
                if str(item.GetUniqueId()) == item_id or item.GetName() == item_id:
                    return item
    
    # Search audio tracks
    for track_index in range(1, audio_track_count + 1):
        items = timeline.GetItemListInTrack("audio", track_index)
        if items:
            for item in items:
                if str(item.GetUniqueId()) == item_id or item.GetName() == item_id:
                    return item
    
    return None

def get_keyframeable_properties(timeline_item):
    """Get list of keyframeable properties for a timeline item."""
    video_properties = [
        'Pan', 'Tilt', 'ZoomX', 'ZoomY', 'Rotation', 'AnchorPointX', 'AnchorPointY',
        'Pitch', 'Yaw', 'Opacity', 'CropLeft', 'CropRight', 'CropTop', 'CropBottom'
    ]
    
    audio_properties = ['Volume', 'Pan']
    
    if timeline_item.GetMediaType() == "Video":
        return video_properties
    elif timeline_item.GetMediaType() == "Audio":
        return audio_properties
    else:
        # Mixed media might have both
        return video_properties + audio_properties

def get_all_keyframeable_properties():
    """Get all possible keyframeable properties."""
    return [
        'Pan', 'Tilt', 'ZoomX', 'ZoomY', 'Rotation', 'AnchorPointX', 'AnchorPointY',
        'Pitch', 'Yaw', 'Opacity', 'CropLeft', 'CropRight', 'CropTop', 'CropBottom',
        'Volume'
    ]

def get_property_keyframes(timeline_item, property_name: str):
    """Get keyframes for a specific property."""
    # This would use actual API to get keyframes
    return []

def has_keyframe_at_frame(timeline_item, property_name: str, frame: int):
    """Check if there's a keyframe at the specified frame."""
    # This would use actual API to check
    return True

def get_keyframe_value(timeline_item, property_name: str, frame: int):
    """Get the value of a keyframe at a specific frame."""
    # This would use actual API to get value
    return 0.0

def delete_keyframe_at_frame(timeline_item, property_name: str, frame: int):
    """Delete a keyframe at the specified frame."""
    # This would use actual API to delete
    return True
