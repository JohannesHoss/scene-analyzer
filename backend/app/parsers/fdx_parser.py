"""
FDX Parser - Final Draft XML Format
"""
import re
from typing import Optional
from xml.etree import ElementTree as ET

from app.models.scene import Scene
from app.parsers.base import BaseParser
from app.parsers.exceptions import ParsingError


class FDXParser(BaseParser):
    """Parser für Final Draft (.fdx) XML-Format."""

    SCENE_HEADING_PATTERN = re.compile(
        r"^(INT\./EXT|INT/EXT|INNEN/AUSSEN|INNEN\.?/AUSSEN\.?|I/E|INT\.?|EXT\.?|INNEN\.?|AUSSEN\.?)"
        r"[\s]+(.+?)(?:\s+-\s+(.+))?$",
        re.IGNORECASE,
    )

    def can_parse(self, filename: str, content: bytes) -> bool:
        if filename.lower().endswith(".fdx"):
            return True
        # Check for FinalDraft XML marker
        try:
            text = content.decode("utf-8", errors="ignore")[:500]
            return "FinalDraft" in text and "<?xml" in text
        except Exception:
            return False

    def parse(self, content: bytes) -> list[Scene]:
        try:
            root = ET.fromstring(content.decode("utf-8"))
            return self._extract_scenes_from_xml(root)
        except Exception as e:
            raise ParsingError(f"FDX parsing failed: {e}", format_type="fdx")

    def _normalize_int_ext(self, value: str) -> str:
        v = value.upper().replace(".", "")
        if v in ("INT/EXT", "INNEN/AUSSEN", "I/E"):
            return "INT/EXT"
        if v == "INNEN":
            return "INT"
        if v == "AUSSEN":
            return "EXT"
        if v in ("INT", "EXT"):
            return v
        return value.upper()

    def _extract_scenes_from_xml(self, root: ET.Element) -> list[Scene]:
        """Extrahiert Szenen aus FDX XML."""
        scenes: list[Scene] = []
        current_scene: Optional[Scene] = None
        current_content: list[str] = []
        scene_number = 1
        line_number = 0

        # Find all Paragraph elements
        for para in root.findall(".//Paragraph"):
            line_number += 1
            para_type = para.get("Type", "")
            text = self._extract_text_from_paragraph(para)

            if para_type == "Scene Heading":
                # Close previous scene
                if current_scene:
                    current_scene.raw_content = "\n".join(current_content)
                    scenes.append(current_scene)
                    current_content = []

                # Parse scene heading
                m = self.SCENE_HEADING_PATTERN.match(text)
                if m:
                    int_ext = self._normalize_int_ext(m.group(1))
                    location = (m.group(2) or "UNKNOWN").strip()
                    time = m.group(3) or None
                else:
                    # Fallback: Try to extract INT/EXT from text
                    int_ext = "INT" if "INT" in text.upper() else "EXT"
                    location = text.split("-")[0].strip() if "-" in text else text.strip()
                    time = text.split("-")[1].strip() if "-" in text else None

                page_number = self._estimate_page(line_number, 1000)  # rough estimate
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
                # Add content to current scene
                if text.strip():
                    current_content.append(text)

        # Close last scene
        if current_scene:
            current_scene.raw_content = "\n".join(current_content)
            scenes.append(current_scene)

        return scenes

    def _extract_text_from_paragraph(self, para: ET.Element) -> str:
        """Extrahiert Text aus einem Paragraph-Element."""
        parts: list[str] = []

        # Get text from Text elements
        for text_elem in para.findall(".//Text"):
            if text_elem.text:
                parts.append(text_elem.text)

        return "".join(parts)

    def _extract_characters(self, content: str) -> list[str]:
        """Extrahiert Charakternamen (einfache Heuristik)."""
        chars: set[str] = set()
        lines = content.split("\n")

        for line in lines:
            line = line.strip()
            # Character names are usually ALL CAPS on their own line
            if line and line.isupper() and 2 <= len(line) <= 30:
                if not line.isdigit():
                    # Remove parentheticals
                    name = re.sub(r"\s*\([^)]+\)", "", line).strip()
                    if name:
                        chars.add(name)

        return sorted(list(chars))
