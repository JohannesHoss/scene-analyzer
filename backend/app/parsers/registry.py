"""
Parser Registry - Factory für Script-Parser
"""
from app.parsers.base import BaseParser
from app.parsers.exceptions import UnsupportedFormatError
from app.parsers.fountain_parser import FountainParser


class ParserRegistry:
    """Registry für alle verfügbaren Parser."""

    def __init__(self):
        # Parser in Prioritäts-Reihenfolge
        self.parsers: list[BaseParser] = [
            FountainParser(),
            # PlainTextParser() wird in Phase 2 hinzugefügt
        ]

    def get_parser(self, filename: str, content: bytes) -> BaseParser:
        """
        Findet passenden Parser basierend auf Dateiname und Content.

        Args:
            filename: Dateiname
            content: Erste bytes der Datei (für Content-Detection)

        Returns:
            Passender Parser

        Raises:
            UnsupportedFormatError: Wenn kein Parser gefunden wurde
        """
        # Prüfe ersten 1 KB für Content-basierte Detection
        sample = content[:1024]

        for parser in self.parsers:
            if parser.can_parse(filename, sample):
                return parser

        # Kein passender Parser gefunden
        supported_formats = ["fountain"]  # TODO: Dynamisch aus Parsern extrahieren
        raise UnsupportedFormatError(filename, supported_formats)

    def get_format_name(self, parser: BaseParser) -> str:
        """
        Gibt den Format-Namen für einen Parser zurück.

        Args:
            parser: Parser-Instanz

        Returns:
            Format-Name (z.B. "fountain")
        """
        class_name = parser.__class__.__name__
        # Entferne "Parser" Suffix
        return class_name.replace("Parser", "").lower()
