"""Custom exceptions for the EPANET PySide6 application."""

class InputFileError(Exception):
    """Custom exception for errors encountered while parsing an EPANET input file."""
    def __init__(self, message, errors=None):
        super().__init__(message)
        self.errors = errors if errors is not None else []
