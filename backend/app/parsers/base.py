"""
Base Parser - Abstract Base Class für alle Script-Parser
"""
from abc import ABC, abstractmethod

from app.models.scene import Scene


class BaseParser(ABC):
    """Basis-Klasse für alle Format-Parser."""

    @abstractmethod
    def parse(self, content: bytes) -> list[Scene]:
        """
        Parst den Drehbuch-Content und gibt Liste von Szenen zurück.

        Args:
            content: Datei-Content als bytes

        Returns:
            Liste von Scene-Objekten

        Raises:
            ParsingError: Bei Parsing-Fehlern
        """
        pass

    @abstractmethod
    def can_parse(self, filename: str, content: bytes) -> bool:
        """
        Prüft, ob dieser Parser das Format verarbeiten kann.

        Args:
            filename: Dateiname
            content: Datei-Content (erste 1024 bytes für Detection)

        Returns:
            True wenn Parser zuständig ist
        """
        pass

    def _estimate_page(self, line_number: int, total_lines: int, lines_per_page: int = 55) -> int:
        """
        Schätzt Seitenzahl basierend auf Zeilen.

        Standard: 55 Zeilen ≈ 1 Seite (Drehbuch-Standard)

        Args:
            line_number: Aktuelle Zeile
            total_lines: Gesamtzahl Zeilen
            lines_per_page: Zeilen pro Seite (Standard: 55)

        Returns:
            Geschätzte Seitenzahl (min. 1)
        """
        return max(1, line_number // lines_per_page)

    def _estimate_length(self, page_count: int, minutes_per_page: float = 1.0) -> float:
        """
        Schätzt Szenen-Länge basierend auf Seitenzahl.

        Standard: 1 Seite ≈ 1 Minute

        Args:
            page_count: Anzahl Seiten
            minutes_per_page: Minuten pro Seite (Standard: 1.0)

        Returns:
            Geschätzte Länge in Minuten
        """
        return round(page_count * minutes_per_page, 1)
