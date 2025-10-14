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
            scenes=scenes,  # Include full scenes data
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

    def _detect_language(self, scenes) -> str:
        """
        Erkennt Sprache des Drehbuchs (DE oder EN).

        Args:
            scenes: Liste von Scenes

        Returns:
            "de" oder "en"
        """
        if not scenes:
            return "de"  # Default

        # Prüfe ersten Scene-Heading
        first_int_ext = scenes[0].int_ext or ""

        # Deutsche Keywords in raw_content?
        german_keywords = ["INNEN", "AUSSEN", "MORGEN", "ABEND"]
        for scene in scenes[:3]:  # Prüfe erste 3 Szenen
            if scene.raw_content:
                content_upper = scene.raw_content.upper()
                if any(keyword in content_upper for keyword in german_keywords):
                    return "de"

        return "de"  # Default Deutsch

    async def _analyze_scenes_with_ai(self, scenes, language: str):
        """
        Analysiert Szenen mit KI und fügt summary, subtext, scene_goal hinzu.

        Args:
            scenes: Liste von Scenes (wird in-place modifiziert)
            language: Sprache (de oder en)
        """
        try:
            analyses = await self.ai_analyzer.analyze_scenes_batch(scenes, language)

            for scene, analysis in zip(scenes, analyses):
                scene.summary = analysis.get("summary")
                scene.subtext = analysis.get("subtext")
                scene.scene_goal = analysis.get("scene_goal")
        except Exception as e:
            # Bei Fehler: Fallback ohne KI
            print(f"AI analysis failed: {e}")
            for scene in scenes:
                if scene.raw_content:
                    # Einfacher Fallback: Erste Zeilen als Summary
                    lines = scene.raw_content.strip().split("\n")[:2]
                    scene.summary = " ".join(lines)[:150]
