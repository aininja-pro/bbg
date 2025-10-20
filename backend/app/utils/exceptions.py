"""Custom exceptions for BBG application."""


class BBGException(Exception):
    """Base exception for BBG application."""
    pass


class ExcelProcessingError(BBGException):
    """Exception raised during Excel file processing."""
    pass


class ValidationError(BBGException):
    """Exception raised during data validation."""
    pass


class LookupError(BBGException):
    """Exception raised during lookup table operations."""
    pass


class TransformationError(BBGException):
    """Exception raised during data transformation."""
    pass
