"""
Fountain Parser - Parser für Fountain-Format (.fountain)

Fountain Spec: https://fountain.io/syntax
"""
import re
from typing import Optional

from app.models.scene import Scene
from app.parsers.base import BaseParser
from app.parsers.exceptions import ParsingError


class FountainParser(BaseParser):
    """Parser für Fountain-Format (.fountain)."""

    # Scene Heading Pattern: INT./EXT. LOCATION - TIME
    # Längste Matches zuerst (wichtig für Regex-Reihenfolge!)
    SCENE_HEADING_PATTERN = re.compile(
        r"^(INT\./EXT|INT/EXT|I/E|INT|EXT)[\.\s]+(.+?)(?:\s+-\s+(.+))?$", re.IGNORECASE | re.MULTILINE
    )

    # Character Pattern: ALL CAPS (min. 2 Zeichen), optional mit Parentheticals
    CHARACTER_PATTERN = re.compile(r"^([A-ZÄÖÜ][A-ZÄÖÜ\s]{1,})(?:\s*\([^)]+\))?\s*$", re.MULTILINE)

    def can_parse(self, filename: str, content: bytes) -> bool:
        """
        Prüft ob Fountain-Format vorliegt.

        Kriterien:
        - Dateiname endet auf .fountain ODER
        - Content enthält Scene Headings (INT./EXT.)
        """
        if filename.lower().endswith(".fountain"):
            return True

        try:
            text = content.decode("utf-8", errors="ignore")
            return bool(self.SCENE_HEADING_PATTERN.search(text))
        except Exception:
            return False

    def parse(self, content: bytes) -> list[Scene]:
        """
        Parst Fountain-Content und extrahiert Szenen.

        Args:
            content: Fountain-Datei als bytes

        Returns:
            Liste von Scene-Objekten

        Raises:
            ParsingError: Bei Parsing-Fehlern
        """
        try:
            text = content.decode("utf-8")
            scenes = self._extract_scenes(text)
            return scenes
        except Exception as e:
            raise ParsingError(f"Fountain parsing failed: {e}", format_type="fountain")

    def _extract_scenes(self, text: str) -> list[Scene]:
        """
        Extrahiert Szenen aus Fountain-Text.

        Args:
            text: Fountain-Text

        Returns:
            Liste von Scene-Objekten
        """
        scenes: list[Scene] = []
        lines = text.split("\n")
        current_scene: Optional[Scene] = None
        current_scene_content: list[str] = []
        scene_number = 1

        for i, line in enumerate(lines):
            stripped_line = line.strip()

            # Scene Heading erkennen
            match = self.SCENE_HEADING_PATTERN.match(stripped_line)
            if match:
                # Vorherige Szene abschließen
                if current_scene:
                    current_scene.raw_content = "\n".join(current_scene_content)
                    scenes.append(current_scene)
                    current_scene_content = []

                # Neue Szene starten
                int_ext = match.group(1).upper()
                # Normalisiere INT./EXT Varianten
                if int_ext in ["INT./EXT", "INT/EXT", "I/E"]:
                    int_ext = "INT/EXT"

                location = match.group(2).strip() if match.group(2) else "UNKNOWN"
                time = match.group(3).strip() if match.group(3) else None

                page_number = self._estimate_page(i, len(lines))

                current_scene = Scene(
                    scene_number=scene_number,
                    int_ext=int_ext,
                    location=location,
                    time=time,
                    page_number=page_number,
                    characters=[],
                )
                scene_number += 1
            elif current_scene:
                # Content zur aktuellen Szene hinzufügen
                current_scene_content.append(line)

        # Letzte Szene abschließen
        if current_scene:
            current_scene.raw_content = "\n".join(current_scene_content)
            scenes.append(current_scene)

        return scenes

    def _extract_characters(self, content: str) -> list[str]:
        """
        Extrahiert Charakternamen aus Szenen-Content.

        Charaktere sind in Fountain ALL CAPS und stehen alleine auf einer Zeile.

        Args:
            content: Szenen-Content

        Returns:
            Liste eindeutiger Charakternamen
        """
        characters: set[str] = set()

        for match in self.CHARACTER_PATTERN.finditer(content):
            name = match.group(1).strip()

            # Filter: Min 2 Zeichen, max 30 Zeichen, keine reinen Zahlen
            if 2 <= len(name) <= 30 and not name.isdigit():
                # Entferne Parentheticals (z.B. "ANNA (O.S.)")
                name = re.sub(r"\s*\([^)]+\)", "", name).strip()
                if name:
                    characters.add(name)

        return sorted(list(characters))
