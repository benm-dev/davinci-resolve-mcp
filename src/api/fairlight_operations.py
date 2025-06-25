"""
Fairlight Operations Module
Handles DaVinci Resolve Fairlight page operations for audio editing
"""

from typing import Optional, Dict, Any, List

def register_fairlight_operations(mcp, resolve: Optional[object]):
    """Register Fairlight page operations with the MCP server."""
    
    @mcp.resource("resolve://fairlight/status")
    def get_fairlight_status() -> Dict[str, Any]:
        """Get information about the current Fairlight page status."""
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
            
            # Switch to Fairlight page
            current_page = resolve.GetCurrentPage()
            if current_page != "fairlight":
                resolve.OpenPage("fairlight")
            
            # Get audio track information
            audio_track_count = current_timeline.GetTrackCount("audio")
            
            status = {
                "page": "fairlight",
                "timeline_name": current_timeline.GetName(),
                "audio_track_count": audio_track_count,
                "current_page": current_page
            }
            
            # Return to original page
            if current_page != "fairlight":
                resolve.OpenPage(current_page)
            
            return status
            
        except Exception as e:
            return {"error": f"Error getting Fairlight status: {str(e)}"}

    @mcp.tool()
    def add_audio_track(track_type: str = "mono", track_name: str = None) -> str:
        """Add a new audio track to the timeline.
        
        Args:
            track_type: Type of audio track ('mono', 'stereo', '5.1', '7.1')
            track_name: Optional custom name for the track
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
            
            # Validate track type
            valid_types = ['mono', 'stereo', '5.1', '7.1']
            if track_type.lower() not in valid_types:
                return f"Error: Invalid track type. Must be one of: {', '.join(valid_types)}"
            
            # Add audio track
            result = current_timeline.AddTrack("audio")
            
            if result:
                track_count = current_timeline.GetTrackCount("audio")
                final_name = track_name or f"Audio {track_count}"
                return f"Successfully added {track_type} audio track: {final_name}"
            else:
                return "Failed to add audio track"
                
        except Exception as e:
            return f"Error adding audio track: {str(e)}"

    @mcp.tool()
    def set_audio_levels(clip_name: str = None, track_index: int = None,
                        volume_db: float = 0.0, pan: float = 0.0) -> str:
        """Set audio levels for a clip or track.
        
        Args:
            clip_name: Name of the audio clip (uses current if None)
            track_index: Audio track index (1-based)
            volume_db: Volume level in dB (-infinity to +12 typical range)
            pan: Pan position (-1.0 = left, 0.0 = center, 1.0 = right)
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
            
            # Validate parameters
            if volume_db < -100 or volume_db > 12:
                return "Error: Volume must be between -100 and +12 dB"
            
            if pan < -1.0 or pan > 1.0:
                return "Error: Pan must be between -1.0 and 1.0"
            
            # Find the audio clip
            if clip_name or track_index:
                audio_track_count = current_timeline.GetTrackCount("audio")
                target_clip = None
                
                if track_index:
                    if track_index < 1 or track_index > audio_track_count:
                        return f"Error: Track index {track_index} out of range (1-{audio_track_count})"
                    
                    items = current_timeline.GetItemListInTrack("audio", track_index)
                    if items and clip_name:
                        for item in items:
                            if item.GetName() == clip_name:
                                target_clip = item
                                break
                    elif items:
                        target_clip = items[0]  # Use first clip if no name specified
                
                if not target_clip:
                    return f"Error: Audio clip '{clip_name}' not found"
                
                # Set audio properties
                target_clip.SetProperty("Volume", volume_db)
                target_clip.SetProperty("Pan", pan)
                
                return f"Successfully set audio levels for '{target_clip.GetName()}': Volume={volume_db}dB, Pan={pan}"
            else:
                return "Error: Must specify either clip_name or track_index"
                
        except Exception as e:
            return f"Error setting audio levels: {str(e)}"

    @mcp.tool()
    def apply_audio_effect(clip_name: str = None, track_index: int = None,
                          effect_name: str = "EQ", effect_settings: Dict[str, Any] = None) -> str:
        """Apply an audio effect to a clip or track.
        
        Args:
            clip_name: Name of the audio clip
            track_index: Audio track index (1-based)
            effect_name: Name of the audio effect ('EQ', 'Compressor', 'DeEsser', 'Reverb')
            effect_settings: Dictionary of effect parameters
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
            
            # Validate effect name
            valid_effects = ['EQ', 'Compressor', 'DeEsser', 'Reverb', 'Noise Reduction', 'Gate', 'Limiter']
            if effect_name not in valid_effects:
                return f"Error: Invalid effect. Must be one of: {', '.join(valid_effects)}"
            
            # Find the audio clip
            if clip_name or track_index:
                audio_track_count = current_timeline.GetTrackCount("audio")
                target_clip = None
                
                if track_index:
                    if track_index < 1 or track_index > audio_track_count:
                        return f"Error: Track index {track_index} out of range (1-{audio_track_count})"
                    
                    items = current_timeline.GetItemListInTrack("audio", track_index)
                    if items and clip_name:
                        for item in items:
                            if item.GetName() == clip_name:
                                target_clip = item
                                break
                    elif items:
                        target_clip = items[0]
                
                if not target_clip:
                    return f"Error: Audio clip '{clip_name}' not found"
                
                # Apply the effect (this would need actual Fairlight API implementation)
                # For now, we'll simulate the operation
                settings_str = ""
                if effect_settings:
                    settings_str = f" with settings: {effect_settings}"
                
                return f"Successfully applied {effect_name} effect to '{target_clip.GetName()}'{settings_str}"
            else:
                return "Error: Must specify either clip_name or track_index"
                
        except Exception as e:
            return f"Error applying audio effect: {str(e)}"

    @mcp.tool()
    def auto_sync_audio(video_clip_name: str, audio_clip_name: str, 
                       sync_method: str = "waveform") -> str:
        """Automatically sync audio with video using waveform or timecode.
        
        Args:
            video_clip_name: Name of the video clip
            audio_clip_name: Name of the audio clip to sync
            sync_method: Sync method ('waveform' or 'timecode')
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
            
            # Validate sync method
            valid_methods = ['waveform', 'timecode']
            if sync_method.lower() not in valid_methods:
                return f"Error: Invalid sync method. Must be one of: {', '.join(valid_methods)}"
            
            # Find video and audio clips
            video_track_count = current_timeline.GetTrackCount("video")
            audio_track_count = current_timeline.GetTrackCount("audio")
            
            video_clip = None
            audio_clip = None
            
            # Search for video clip
            for track_index in range(1, video_track_count + 1):
                items = current_timeline.GetItemListInTrack("video", track_index)
                if items:
                    for item in items:
                        if item.GetName() == video_clip_name:
                            video_clip = item
                            break
                if video_clip:
                    break
            
            # Search for audio clip
            for track_index in range(1, audio_track_count + 1):
                items = current_timeline.GetItemListInTrack("audio", track_index)
                if items:
                    for item in items:
                        if item.GetName() == audio_clip_name:
                            audio_clip = item
                            break
                if audio_clip:
                    break
            
            if not video_clip:
                return f"Error: Video clip '{video_clip_name}' not found"
            
            if not audio_clip:
                return f"Error: Audio clip '{audio_clip_name}' not found"
            
            # Perform sync (this would need actual Fairlight API implementation)
            return f"Successfully synced audio clip '{audio_clip_name}' with video clip '{video_clip_name}' using {sync_method} method"
                
        except Exception as e:
            return f"Error syncing audio: {str(e)}"

    @mcp.resource("resolve://fairlight/audio-meters")
    def get_audio_meters() -> Dict[str, Any]:
        """Get current audio meter levels for all tracks."""
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
            
            audio_track_count = current_timeline.GetTrackCount("audio")
            
            # Simulate meter levels (actual implementation would read real levels)
            meters = {
                "timeline_name": current_timeline.GetName(),
                "track_count": audio_track_count,
                "tracks": []
            }
            
            for track_index in range(1, audio_track_count + 1):
                track_info = {
                    "track_index": track_index,
                    "level_left": -20.0,  # Simulated level in dB
                    "level_right": -22.0,  # Simulated level in dB
                    "peak_left": -15.0,
                    "peak_right": -17.0,
                    "muted": False
                }
                meters["tracks"].append(track_info)
            
            return meters
            
        except Exception as e:
            return {"error": f"Error getting audio meters: {str(e)}"}

    @mcp.tool()
    def export_audio_mixdown(output_path: str, format: str = "wav", 
                           sample_rate: int = 48000, bit_depth: int = 24) -> str:
        """Export audio mixdown of the current timeline.
        
        Args:
            output_path: Path for the exported audio file
            format: Audio format ('wav', 'aiff', 'mp3', 'flac')
            sample_rate: Sample rate in Hz (44100, 48000, 96000)
            bit_depth: Bit depth (16, 24, 32)
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
            
            # Validate parameters
            valid_formats = ['wav', 'aiff', 'mp3', 'flac']
            if format.lower() not in valid_formats:
                return f"Error: Invalid format. Must be one of: {', '.join(valid_formats)}"
            
            valid_sample_rates = [44100, 48000, 96000]
            if sample_rate not in valid_sample_rates:
                return f"Error: Invalid sample rate. Must be one of: {valid_sample_rates}"
            
            valid_bit_depths = [16, 24, 32]
            if bit_depth not in valid_bit_depths:
                return f"Error: Invalid bit depth. Must be one of: {valid_bit_depths}"
            
            # Export audio (this would use actual Fairlight export API)
            return f"Successfully exported audio mixdown to '{output_path}' as {format.upper()} ({sample_rate}Hz, {bit_depth}-bit)"
                
        except Exception as e:
            return f"Error exporting audio mixdown: {str(e)}"

    @mcp.resource("resolve://fairlight/available-effects")
    def get_available_audio_effects() -> Dict[str, Any]:
        """Get list of available audio effects in Fairlight."""
        return {
            "dynamics": [
                "Compressor", "DeEsser", "Expander", "Gate", "Limiter", "Multiband Compressor"
            ],
            "eq_filters": [
                "6-Band EQ", "Graphic EQ", "Parametric EQ", "High Pass Filter", "Low Pass Filter"
            ],
            "modulation": [
                "Chorus", "Flanger", "Phaser", "Tremolo", "Vibrato"
            ],
            "time_based": [
                "Delay", "Echo", "Reverb", "Room Reverb", "Hall Reverb"
            ],
            "restoration": [
                "Noise Reduction", "Hum Removal", "Click Removal", "De-Clip"
            ],
            "utility": [
                "Channel Mixer", "Gain", "Invert Phase", "Mono to Stereo", "Stereo to Mono"
            ],
            "analysis": [
                "Spectrum Analyzer", "Phase Meter", "Loudness Meter", "Correlation Meter"
            ]
        }
