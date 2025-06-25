"""
DaVinci Resolve MCP Utilities Package
Provides common utilities for the MCP server
"""

from .page_manager import ensure_page, get_valid_pages, validate_page_name
from .response_formatter import success, error, info, legacy_success, legacy_error
from .validation import (
    ValidationError, validate_range, validate_choice, validate_file_path,
    validate_directory_path, validate_file_extension, validate_resolve_connection,
    validate_positive_integer, validate_non_empty_string, validate_params
)
from .error_handler import (
    ResolveError, ConnectionError, OperationError, handle_resolve_errors,
    log_operation, validate_resolve_state, get_project_state, create_context_error
)
from .resolve_helpers import (
    get_current_project, get_current_timeline, get_media_pool,
    find_clip_by_name, find_folder_by_name, get_timeline_item_by_name,
    get_all_media_pool_clips, get_all_media_pool_folders,
    safe_get_attribute, safe_call_method, format_timecode, parse_timecode
)
from .fusion_utils import (
    get_fusion_comp, set_node_input, set_node_attributes,
    find_node, get_node_info, connect_nodes, validate_node_type,
    validate_blend_mode, get_available_blend_modes, get_node_categories
)

__all__ = [
    # Page manager
    'ensure_page', 'get_valid_pages', 'validate_page_name',
    
    # Response formatting
    'success', 'error', 'info', 'legacy_success', 'legacy_error',
    
    # Validation
    'ValidationError', 'validate_range', 'validate_choice', 'validate_file_path',
    'validate_directory_path', 'validate_file_extension', 'validate_resolve_connection',
    'validate_positive_integer', 'validate_non_empty_string', 'validate_params',
    
    # Error handling
    'ResolveError', 'ConnectionError', 'OperationError', 'handle_resolve_errors',
    'log_operation', 'validate_resolve_state', 'get_project_state', 'create_context_error',
    
    # Resolve helpers
    'get_current_project', 'get_current_timeline', 'get_media_pool',
    'find_clip_by_name', 'find_folder_by_name', 'get_timeline_item_by_name',
    'get_all_media_pool_clips', 'get_all_media_pool_folders',
    'safe_get_attribute', 'safe_call_method', 'format_timecode', 'parse_timecode',
    
    # Fusion utilities
    'get_fusion_comp', 'set_node_input', 'set_node_attributes',
    'find_node', 'get_node_info', 'connect_nodes', 'validate_node_type',
    'validate_blend_mode', 'get_available_blend_modes', 'get_node_categories'
]
