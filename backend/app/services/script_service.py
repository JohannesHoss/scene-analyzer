"""
Script Service - Business Logic für Script-Upload und -Verarbeitung
"""
import uuid
from datetime import datetime

from fastapi import UploadFile

from app.models.api import ScriptUploadResponse
from app.parsers.registry import ParserRegistry


class ScriptService:
    """Service für Script-Upload und -Verarbeitung."""

    def __init__(self):
        self.parser_registry = ParserRegistry()

    async def upload_and_parse(self, file: UploadFile) -> ScriptUploadResponse:
        """
        Lädt Script hoch, parst es und gibt Metadaten zurück.

        Args:
            file: Hochgeladene Datei

        Returns:
            Script-Metadaten

        Raises:
            UnsupportedFormatError: Bei nicht unterstütztem Format
            ParsingError: Bei Parsing-Fehlern
        """
        # Datei einlesen
        content = await file.read()

        # Parser finden
        parser = self.parser_registry.get_parser(file.filename or "unknown", content)

        # Parsen
        scenes = parser.parse(content)

        # Format-Name
        format_name = self.parser_registry.get_format_name(parser)

        # Metadaten berechnen
        pages = self._calculate_pages(scenes)

        # Response erstellen
        return ScriptUploadResponse(
            script_id=self._generate_id(),
            filename=file.filename or "unknown",
            format=format_name,
            scenes_count=len(scenes),
            pages=pages,
            upload_time=datetime.utcnow(),
        )

    def _calculate_pages(self, scenes) -> int:
        """
        Berechnet Gesamtseitenzahl aus Szenen.

        Args:
            scenes: Liste von Scene-Objekten

        Returns:
            Maximale Seitenzahl (0 wenn keine Szenen)
        """
        if not scenes:
            return 0
        return max(scene.page_number for scene in scenes)

    def _generate_id(self) -> str:
        """
        Generiert eindeutige UUID für Script.

        Returns:
            UUID als String
        """
        return str(uuid.uuid4())
