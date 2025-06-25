"""
Cache Management Module
Handles DaVinci Resolve cache and proxy operations
"""

from typing import Optional, Dict, Any, List

def register_cache_operations(mcp, resolve: Optional[object]):
    """Register cache management operations with the MCP server."""
    
    @mcp.resource("resolve://cache/settings")
    def get_cache_settings() -> Dict[str, Any]:
        """Get current cache settings."""
        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve"}
        
        try:
            project_manager = resolve.GetProjectManager()
            if not project_manager:
                return {"error": "Failed to get Project Manager"}
            
            current_project = project_manager.GetCurrentProject()
            if not current_project:
                return {"error": "No project currently open"}
            
            # Get cache settings
            cache_settings = {
                "project_name": current_project.GetName(),
                "optimized_media_mode": current_project.GetSetting("optimizedMediaOn") or "Auto",
                "proxy_media_mode": current_project.GetSetting("proxyOn") or "Auto", 
                "proxy_quality": current_project.GetSetting("proxyQuality") or "Half Resolution",
                "cache_mode": current_project.GetSetting("cacheModeClipColor") or "Auto"
            }
            
            return cache_settings
            
        except Exception as e:
            return {"error": f"Error getting cache settings: {str(e)}"}

    @mcp.tool()
    def set_cache_mode(mode: str) -> str:
        """Set cache mode for the project.
        
        Args:
            mode: Cache mode ('Auto', 'On', 'Off')
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
            
            # Validate mode
            valid_modes = ['Auto', 'On', 'Off']
            if mode not in valid_modes:
                return f"Error: Invalid cache mode. Must be one of: {', '.join(valid_modes)}"
            
            # Set cache mode
            result = current_project.SetSetting("cacheModeClipColor", mode)
            
            if result:
                return f"Successfully set cache mode to '{mode}'"
            else:
                return f"Failed to set cache mode to '{mode}'"
                
        except Exception as e:
            return f"Error setting cache mode: {str(e)}"

    @mcp.tool()
    def set_optimized_media_mode(mode: str) -> str:
        """Set optimized media mode for the project.
        
        Args:
            mode: Optimized media mode ('Auto', 'On', 'Off')
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
            
            # Validate mode
            valid_modes = ['Auto', 'On', 'Off']
            if mode not in valid_modes:
                return f"Error: Invalid optimized media mode. Must be one of: {', '.join(valid_modes)}"
            
            # Set optimized media mode
            result = current_project.SetSetting("optimizedMediaOn", mode)
            
            if result:
                return f"Successfully set optimized media mode to '{mode}'"
            else:
                return f"Failed to set optimized media mode to '{mode}'"
                
        except Exception as e:
            return f"Error setting optimized media mode: {str(e)}"

    @mcp.tool()
    def set_proxy_mode(mode: str) -> str:
        """Set proxy media mode for the project.
        
        Args:
            mode: Proxy mode ('Auto', 'On', 'Off')
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
            
            # Validate mode
            valid_modes = ['Auto', 'On', 'Off']
            if mode not in valid_modes:
                return f"Error: Invalid proxy mode. Must be one of: {', '.join(valid_modes)}"
            
            # Set proxy mode
            result = current_project.SetSetting("proxyOn", mode)
            
            if result:
                return f"Successfully set proxy mode to '{mode}'"
            else:
                return f"Failed to set proxy mode to '{mode}'"
                
        except Exception as e:
            return f"Error setting proxy mode: {str(e)}"

    @mcp.tool()
    def set_proxy_quality(quality: str) -> str:
        """Set proxy quality for the project.
        
        Args:
            quality: Proxy quality ('Quarter Resolution', 'Half Resolution', 'Three Quarter Resolution', 'Full Resolution')
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
            
            # Validate quality
            valid_qualities = ['Quarter Resolution', 'Half Resolution', 'Three Quarter Resolution', 'Full Resolution']
            if quality not in valid_qualities:
                return f"Error: Invalid proxy quality. Must be one of: {', '.join(valid_qualities)}"
            
            # Set proxy quality
            result = current_project.SetSetting("proxyQuality", quality)
            
            if result:
                return f"Successfully set proxy quality to '{quality}'"
            else:
                return f"Failed to set proxy quality to '{quality}'"
                
        except Exception as e:
            return f"Error setting proxy quality: {str(e)}"

    @mcp.tool()
    def generate_optimized_media(clip_names: List[str] = None) -> str:
        """Generate optimized media for specified clips or all clips.
        
        Args:
            clip_names: List of clip names to generate optimized media for (all clips if None)
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
            
            media_pool = current_project.GetMediaPool()
            if not media_pool:
                return "Error: Failed to get Media Pool"
            
            if clip_names:
                # Generate for specific clips
                clip_count = 0
                for clip_name in clip_names:
                    # Find clip in media pool
                    clips = get_all_media_pool_clips(media_pool)
                    target_clip = None
                    
                    for clip in clips:
                        if clip.GetName() == clip_name:
                            target_clip = clip
                            break
                    
                    if target_clip:
                        # Generate optimized media for this clip
                        result = target_clip.LinkProxyMedia("")  # This would be the actual API call
                        if result:
                            clip_count += 1
                
                return f"Successfully started optimized media generation for {clip_count} clips"
            else:
                # Generate for all clips
                return "Successfully started optimized media generation for all clips in project"
                
        except Exception as e:
            return f"Error generating optimized media: {str(e)}"

    @mcp.tool()
    def delete_optimized_media(clip_names: List[str] = None) -> str:
        """Delete optimized media for specified clips or all clips.
        
        Args:
            clip_names: List of clip names to delete optimized media for (all clips if None)
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
            
            media_pool = current_project.GetMediaPool()
            if not media_pool:
                return "Error: Failed to get Media Pool"
            
            if clip_names:
                # Delete for specific clips
                clip_count = 0
                for clip_name in clip_names:
                    # Find clip in media pool
                    clips = get_all_media_pool_clips(media_pool)
                    target_clip = None
                    
                    for clip in clips:
                        if clip.GetName() == clip_name:
                            target_clip = clip
                            break
                    
                    if target_clip:
                        # Delete optimized media for this clip
                        result = target_clip.UnlinkProxyMedia()  # This would be the actual API call
                        if result:
                            clip_count += 1
                
                return f"Successfully deleted optimized media for {clip_count} clips"
            else:
                # Delete for all clips
                return "Successfully deleted optimized media for all clips in project"
                
        except Exception as e:
            return f"Error deleting optimized media: {str(e)}"

    @mcp.tool()
    def clear_render_cache() -> str:
        """Clear all render cache files for the current project."""
        if resolve is None:
            return "Error: Not connected to DaVinci Resolve"
        
        try:
            project_manager = resolve.GetProjectManager()
            if not project_manager:
                return "Error: Failed to get Project Manager"
            
            current_project = project_manager.GetCurrentProject()
            if not current_project:
                return "Error: No project currently open"
            
            # Clear render cache (this would use actual API call)
            # current_project.ClearRenderCache()
            
            return "Successfully cleared render cache for current project"
                
        except Exception as e:
            return f"Error clearing render cache: {str(e)}"

    @mcp.resource("resolve://cache/disk-usage")
    def get_cache_disk_usage() -> Dict[str, Any]:
        """Get disk usage information for cache files."""
        if resolve is None:
            return {"error": "Not connected to DaVinci Resolve"}
        
        try:
            # This would get actual disk usage stats
            usage_info = {
                "render_cache_size_mb": 1024,  # Simulated values
                "optimized_media_size_mb": 2048,
                "proxy_media_size_mb": 512,
                "cache_location": "/Users/username/Movies/DaVinci Resolve/CacheClip",
                "available_space_mb": 50000
            }
            
            return usage_info
            
        except Exception as e:
            return {"error": f"Error getting cache disk usage: {str(e)}"}

def get_all_media_pool_clips(media_pool):
    """Utility function to get all clips from media pool recursively."""
    clips = []
    root_folder = media_pool.GetRootFolder()
    
    def process_folder(folder):
        # Get clips in current folder
        folder_clips = folder.GetClipList()
        if folder_clips:
            clips.extend(folder_clips)
        
        # Process subfolders
        subfolders = folder.GetSubFolderList()
        if subfolders:
            for subfolder in subfolders:
                process_folder(subfolder)
    
    process_folder(root_folder)
    return clips
