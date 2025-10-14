"""
PDF Parser - Heuristische Szenen-Erkennung aus PDF-Text
"""
import re
from typing import Optional

from PyPDF2 import PdfReader

from app.models.scene import Scene
from app.parsers.base import BaseParser


class PDFParser(BaseParser):
    """Parser für PDF-Drehbücher (heuristisch)."""

    # DE + EN Scene Headings
    SCENE_HEADING_PATTERN = re.compile(
        r"^(INT\./EXT|INT/EXT|INNEN/AUSSEN|INNEN\.?/AUSSEN\.?|I/E|INT\.?|EXT\.?|INNEN\.?|AUSSEN\.?)"
        r"[\s]+(.+?)(?:\s+-\s+(.+))?$",
        re.IGNORECASE | re.MULTILINE,
    )

    CHARACTER_PATTERN = re.compile(r"^([A-ZÄÖÜ][A-ZÄÖÜ\s]{1,})(?:\s*\([^)]+\))?\s*$", re.MULTILINE)

    def can_parse(self, filename: str, content: bytes) -> bool:
        if filename.lower().endswith(".pdf"):
            return True
        return content.startswith(b"%PDF")

    def parse(self, content: bytes) -> list[Scene]:
        text = self._extract_text_from_pdf(content)
        return self._extract_scenes_from_text(text)

    def _extract_text_from_pdf(self, content: bytes) -> str:
        """Extrahiert Text aus PDF (einfacher Ansatz)."""
        from io import BytesIO

        reader = PdfReader(BytesIO(content))
        parts: list[str] = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            parts.append(page_text)
        return "\n".join(parts)

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

    def _extract_scenes_from_text(self, text: str) -> list[Scene]:
        scenes: list[Scene] = []
        lines = text.split("\n")
        current_scene: Optional[Scene] = None
        current_content: list[str] = []
        scene_number = 1

        for i, raw in enumerate(lines):
            line = raw.strip()
            m = self.SCENE_HEADING_PATTERN.match(line)
            if m:
                # close previous
                if current_scene:
                    current_scene.raw_content = "\n".join(current_content)
                    scenes.append(current_scene)
                    current_content = []
                int_ext = self._normalize_int_ext(m.group(1))
                location = (m.group(2) or "UNKNOWN").strip()
                time = (m.group(3) or None)
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
                current_content.append(raw)

        if current_scene:
            current_scene.raw_content = "\n".join(current_content)
            scenes.append(current_scene)

        return scenes

    def _extract_characters(self, content: str) -> list[str]:
        chars: set[str] = set()
        for m in self.CHARACTER_PATTERN.finditer(content):
            name = m.group(1).strip()
            if 2 <= len(name) <= 30 and not name.isdigit():
                name = re.sub(r"\s*\([^)]+\)", "", name).strip()
                if name:
                    chars.add(name)
        return sorted(list(chars))
