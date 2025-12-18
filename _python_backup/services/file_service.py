"""
File handling service
"""

from typing import List, Optional
from domain.models import FileUploadInfo
from domain.exceptions import FileError, ValidationError
from config.constants import ALLOWED_FILE_TYPES, MAX_FILE_SIZE_MB


class FileService:
    """Service for file operations"""
    
    @staticmethod
    def validate_file(file_name: str, file_size: int) -> None:
        """
        Validate uploaded file
        
        Args:
            file_name: Name of the file
            file_size: Size of the file in bytes
            
        Raises:
            ValidationError: If file is invalid
        """
        # Check file extension
        if not any(file_name.lower().endswith(ext) for ext in ALLOWED_FILE_TYPES):
            raise ValidationError(
                f"File type not allowed. Allowed types: {', '.join(ALLOWED_FILE_TYPES)}"
            )
        
        # Check file size
        size_mb = file_size / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            raise ValidationError(
                f"File size ({size_mb:.2f} MB) exceeds maximum allowed size "
                f"({MAX_FILE_SIZE_MB} MB)"
            )
    
    @staticmethod
    def read_file_content(uploaded_file) -> str:
        """
        Read content from uploaded file
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            File content as string
            
        Raises:
            FileError: If reading fails
        """
        try:
            return uploaded_file.read().decode('utf-8')
        except Exception as e:
            raise FileError(f"Failed to read file {uploaded_file.name}: {str(e)}") from e
    
    @staticmethod
    def get_file_info(uploaded_file) -> FileUploadInfo:
        """
        Get file information
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            FileUploadInfo domain model
        """
        return FileUploadInfo(
            name=uploaded_file.name,
            size_bytes=len(uploaded_file.getvalue())
        )

