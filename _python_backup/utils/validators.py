"""
Input validation utilities
"""

from typing import List, Any
from domain.exceptions import ValidationError


def validate_file_list(files: List[Any]) -> None:
    """
    Validate that file list is not empty
    
    Args:
        files: List of files
        
    Raises:
        ValidationError: If validation fails
    """
    if not files:
        raise ValidationError("No files provided")
    
    if len(files) == 0:
        raise ValidationError("File list is empty")


def validate_analysis_results(results: Any) -> None:
    """
    Validate that analysis results exist
    
    Args:
        results: Analysis results
        
    Raises:
        ValidationError: If validation fails
    """
    if results is None:
        raise ValidationError("No analysis results available. Please analyze files first.")

