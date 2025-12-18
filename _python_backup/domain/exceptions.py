"""
Domain-specific exceptions
"""


class VNGError(Exception):
    """Base exception for VNG-related errors"""
    pass


class ParsingError(VNGError):
    """Raised when file parsing fails"""
    pass


class AnalysisError(VNGError):
    """Raised when analysis fails"""
    pass


class ValidationError(VNGError):
    """Raised when validation fails"""
    pass


class FileError(VNGError):
    """Raised when file operations fail"""
    pass

