"""
Common Helper Utilities for DaVinci Resolve MCP
Provides reusable helper functions for common operations
"""

import logging
from typing import Any, Dict, List, Optional, Union
from .error_handler import validate_resolve_state, OperationError

logger = logging.getLogger("davinci-resolve-mcp.helpers")

def get_current_project(resolve: Any) -> Any:
    """
    Get the current project with error handling.
    
    Args:
        resolve: DaVinci Resolve instance
    
    Returns:
        Current project object
    
    Raises:
        OperationError: If project cannot be accessed
    """
    validate_resolve_state(resolve)
    
    project_manager = resolve.GetProjectManager()
    if not project_manager:
        raise OperationError("Failed to get Project Manager")
    
    current_project = project_manager.GetCurrentProject()
    if not current_project:
        raise OperationError("No project currently open")
    
    return current_project

def get_current_timeline(resolve: Any) -> Any:
    """
    Get the current timeline with error handling.
    
    Args:
        resolve: DaVinci Resolve instance
    
    Returns:
        Current timeline object
    
    Raises:
        OperationError: If timeline cannot be accessed
    """
    current_project = get_current_project(resolve)
    
    current_timeline = current_project.GetCurrentTimeline()
    if not current_timeline:
        raise OperationError("No timeline currently active")
    
    return current_timeline

def get_media_pool(resolve: Any) -> Any:
    """
    Get the media pool with error handling.
    
    Args:
        resolve: DaVinci Resolve instance
    
    Returns:
        Media pool object
    
    Raises:
        OperationError: If media pool cannot be accessed
    """
    current_project = get_current_project(resolve)
    
    media_pool = current_project.GetMediaPool()
    if not media_pool:
        raise OperationError("Failed to get Media Pool")
    
    return media_pool

def find_clip_by_name(media_pool: Any, clip_name: str, folder: Any = None) -> Optional[Any]:
    """
    Find a clip by name in the media pool.
    
    Args:
        media_pool: Media pool object
        clip_name: Name of the clip to find
        folder: Optional folder to search in (uses root if None)
    
    Returns:
        Clip object if found, None otherwise
    """
    try:
        if folder is None:
            folder = media_pool.GetRootFolder()
        
        # Search in current folder
        clips = folder.GetClipList()
        for clip in clips:
            if clip.GetName() == clip_name:
                return clip
        
        # Search in subfolders
        subfolders = folder.GetSubFolderList()
        for subfolder in subfolders:
            found_clip = find_clip_by_name(media_pool, clip_name, subfolder)
            if found_clip:
                return found_clip
        
        return None
        
    except Exception as e:
        logger.warning(f"Error searching for clip '{clip_name}': {str(e)}")
        return None

def find_folder_by_name(media_pool: Any, folder_name: str, parent_folder: Any = None) -> Optional[Any]:
    """
    Find a folder by name in the media pool.
    
    Args:
        media_pool: Media pool object
        folder_name: Name of the folder to find
        parent_folder: Optional parent folder to search in (uses root if None)
    
    Returns:
        Folder object if found, None otherwise
    """
    try:
        if parent_folder is None:
            parent_folder = media_pool.GetRootFolder()
        
        # Check current folder name
        if parent_folder.GetName() == folder_name:
            return parent_folder
        
        # Search in subfolders
        subfolders = parent_folder.GetSubFolderList()
        for subfolder in subfolders:
            if subfolder.GetName() == folder_name:
                return subfolder
            
            # Recursive search
            found_folder = find_folder_by_name(media_pool, folder_name, subfolder)
            if found_folder:
                return found_folder
        
        return None
        
    except Exception as e:
        logger.warning(f"Error searching for folder '{folder_name}': {str(e)}")
        return None

def get_timeline_item_by_name(timeline: Any, item_name: str, track_type: str = "video") -> Optional[Any]:
    """
    Find a timeline item by name.
    
    Args:
        timeline: Timeline object
        item_name: Name of the item to find
        track_type: Type of track to search ("video" or "audio")
    
    Returns:
        Timeline item if found, None otherwise
    """
    try:
        track_count = timeline.GetTrackCount(track_type)
        
        for track_index in range(1, track_count + 1):
            items = timeline.GetItemListInTrack(track_type, track_index)
            if items:
                for item in items:
                    if item.GetName() == item_name:
                        return item
        
        return None
        
    except Exception as e:
        logger.warning(f"Error searching for timeline item '{item_name}': {str(e)}")
        return None

def get_all_media_pool_clips(media_pool: Any, folder: Any = None) -> List[Any]:
    """
    Get all clips from the media pool recursively.
    
    Args:
        media_pool: Media pool object
        folder: Optional folder to start from (uses root if None)
    
    Returns:
        List of all clips
    """
    clips = []
    
    try:
        if folder is None:
            folder = media_pool.GetRootFolder()
        
        # Get clips from current folder
        folder_clips = folder.GetClipList()
        clips.extend(folder_clips)
        
        # Get clips from subfolders
        subfolders = folder.GetSubFolderList()
        for subfolder in subfolders:
            subfolder_clips = get_all_media_pool_clips(media_pool, subfolder)
            clips.extend(subfolder_clips)
        
    except Exception as e:
        logger.warning(f"Error getting media pool clips: {str(e)}")
    
    return clips

def get_all_media_pool_folders(media_pool: Any, parent_folder: Any = None) -> List[Any]:
    """
    Get all folders from the media pool recursively.
    
    Args:
        media_pool: Media pool object
        parent_folder: Optional parent folder to start from (uses root if None)
    
    Returns:
        List of all folders
    """
    folders = []
    
    try:
        if parent_folder is None:
            parent_folder = media_pool.GetRootFolder()
        
        folders.append(parent_folder)
        
        # Get subfolders recursively
        subfolders = parent_folder.GetSubFolderList()
        for subfolder in subfolders:
            subfolder_list = get_all_media_pool_folders(media_pool, subfolder)
            folders.extend(subfolder_list)
        
    except Exception as e:
        logger.warning(f"Error getting media pool folders: {str(e)}")
    
    return folders

def safe_get_attribute(obj: Any, attr_name: str, default: Any = None) -> Any:
    """
    Safely get an attribute from an object.
    
    Args:
        obj: Object to get attribute from
        attr_name: Name of the attribute
        default: Default value if attribute doesn't exist
    
    Returns:
        Attribute value or default
    """
    try:
        return getattr(obj, attr_name, default)
    except Exception:
        return default

def safe_call_method(obj: Any, method_name: str, *args, **kwargs) -> Any:
    """
    Safely call a method on an object.
    
    Args:
        obj: Object to call method on
        method_name: Name of the method
        *args: Positional arguments
        **kwargs: Keyword arguments
    
    Returns:
        Method result or None if method fails
    """
    try:
        method = getattr(obj, method_name, None)
        if method and callable(method):
            return method(*args, **kwargs)
        return None
    except Exception as e:
        logger.warning(f"Error calling method '{method_name}': {str(e)}")
        return None

def format_timecode(frame: int, fps: float = 24.0) -> str:
    """
    Format a frame number as timecode.
    
    Args:
        frame: Frame number
        fps: Frames per second
    
    Returns:
        Formatted timecode string (HH:MM:SS:FF)
    """
    try:
        total_seconds = frame / fps
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        frames = int(frame % fps)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}:{frames:02d}"
    except Exception:
        return f"Frame {frame}"

def parse_timecode(timecode: str, fps: float = 24.0) -> int:
    """
    Parse a timecode string to frame number.
    
    Args:
        timecode: Timecode string (HH:MM:SS:FF or seconds)
        fps: Frames per second
    
    Returns:
        Frame number
    """
    try:
        if ":" in timecode:
            parts = timecode.split(":")
            if len(parts) == 4:
                hours, minutes, seconds, frames = map(int, parts)
                total_frames = (hours * 3600 + minutes * 60 + seconds) * fps + frames
                return int(total_frames)
        else:
            # Assume it's seconds
            seconds = float(timecode)
            return int(seconds * fps)
    except Exception:
        pass
    
    return 0
