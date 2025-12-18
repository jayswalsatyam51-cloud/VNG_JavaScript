"""
Data formatting utilities
"""

from typing import Optional


def format_number(value: Optional[float], decimals: int = 2) -> str:
    """
    Format a number with specified decimal places
    
    Args:
        value: Number to format
        decimals: Number of decimal places
        
    Returns:
        Formatted string or "N/A" if value is None
    """
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}"


def format_percentage(value: Optional[float], decimals: int = 2) -> str:
    """
    Format a percentage value
    
    Args:
        value: Percentage value
        decimals: Number of decimal places
        
    Returns:
        Formatted string with % sign or "N/A" if value is None
    """
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}%"


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 KB", "2.3 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

