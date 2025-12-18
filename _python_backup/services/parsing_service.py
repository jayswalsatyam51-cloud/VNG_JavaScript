"""
Parsing service for VNG files
"""

from typing import Dict, Any
from domain.models import ParsedFile, MetricValue
from domain.exceptions import ParsingError
from modules.parser import parse_vng_text as _parse_vng_text


class ParsingService:
    """Service for parsing VNG text files"""
    
    @staticmethod
    def parse_file(file_name: str, file_content: str, size_bytes: int = 0) -> ParsedFile:
        """
        Parse a VNG file and return a ParsedFile domain model
        
        Args:
            file_name: Name of the file
            file_content: Raw text content of the file
            size_bytes: Size of the file in bytes
            
        Returns:
            ParsedFile domain model
            
        Raises:
            ParsingError: If parsing fails
        """
        try:
            raw_data = _parse_vng_text(file_content)
            
            # Convert to domain models
            parsed_data: Dict[str, Dict[str, MetricValue]] = {}
            for category, metrics in raw_data.items():
                parsed_data[category] = {
                    metric: MetricValue(
                        value=data['value'],
                        is_flagged=data['is_flagged']
                    )
                    for metric, data in metrics.items()
                }
            
            return ParsedFile(
                name=file_name,
                data=parsed_data,
                size_bytes=size_bytes
            )
        except Exception as e:
            raise ParsingError(f"Failed to parse file {file_name}: {str(e)}") from e
    
    @staticmethod
    def parse_to_dict(file_content: str) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        Parse VNG file content to dictionary format (legacy compatibility)
        
        Args:
            file_content: Raw text content of the file
            
        Returns:
            Dictionary with parsed data
        """
        return _parse_vng_text(file_content)

