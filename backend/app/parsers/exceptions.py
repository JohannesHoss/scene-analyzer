"""
Parser Exceptions - Custom Exceptions für Script-Parsing
"""
from typing import Optional


class ParsingError(Exception):
    """Exception für Parsing-Fehler."""

    def __init__(self, message: str, format_type: str = "unknown"):
        self.message = message
        self.format_type = format_type
        super().__init__(self.message)


class UnsupportedFormatError(Exception):
    """Exception für nicht unterstützte Dateiformate."""

    def __init__(self, filename: str, supported_formats: Optional[list[str]] = None):
        self.filename = filename
        self.supported_formats = supported_formats or ["fountain", "plaintext"]
        self.message = (
            f"Unsupported format for '{filename}'. "
            f"Supported formats: {', '.join(self.supported_formats)}"
        )
        super().__init__(self.message)
