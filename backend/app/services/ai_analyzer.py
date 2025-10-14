"""
AI Analyzer Service - KI-gestützte Szenenanalyse
"""
import asyncio
import json
from typing import Optional

import httpx

from app.config import get_settings
from app.models.scene import Scene


class AIAnalyzer:
    """KI-gestützte Szenenanalyse mit OpenRouter."""

    def __init__(self):
        self.settings = get_settings()
        self.client = httpx.AsyncClient(timeout=30.0)

    async def analyze_scene(self, scene: Scene, language: str = "de") -> dict:
        """
        Analysiert eine Szene mit KI.

        Args:
            scene: Scene-Objekt mit raw_content
            language: Sprache (de oder en)

        Returns:
            Dict mit summary, subtext, scene_goal
        """
        if not self.settings.openrouter_api_key:
            # Fallback ohne KI
            return {
                "summary": self._extract_first_action(scene.raw_content or ""),
                "subtext": "",
                "scene_goal": "",
            }

        try:
            prompt = self._build_prompt(scene, language)
            response = await self._call_openrouter(prompt)
            return self._parse_response(response)

        except Exception as e:
            # Bei Fehler: Fallback
            print(f"AI Analysis failed: {e}")
            return {
                "summary": self._extract_first_action(scene.raw_content or ""),
                "subtext": "Fehler bei KI-Analyse",
                "scene_goal": "Fehler bei KI-Analyse",
            }

    async def analyze_scenes_batch(
        self, scenes: list[Scene], language: str = "de"
    ) -> list[dict]:
        """
        Analysiert mehrere Szenen parallel.

        Args:
            scenes: Liste von Scenes
            language: Sprache

        Returns:
            Liste von Analysis-Dicts
        """
        tasks = [self.analyze_scene(scene, language) for scene in scenes]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        return [
            result
            if not isinstance(result, Exception)
            else {
                "summary": self._extract_first_action(scenes[i].raw_content or ""),
                "subtext": "",
                "scene_goal": "",
            }
            for i, result in enumerate(results)
        ]

    def _build_prompt(self, scene: Scene, language: str) -> str:
        """Erstellt Prompt für KI-Analyse."""
        scene_info = f"""
Szene {scene.scene_number}
{scene.int_ext}. {scene.location} - {scene.time or 'UNKNOWN'}

{scene.raw_content or 'Kein Content'}
"""

        if language == "de":
            return f"""Analysiere folgende Drehbuch-Szene und gib JSON zurück:

{scene_info}

Erstelle eine JSON-Antwort mit:
1. "summary": Kurze Zusammenfassung (1-2 Sätze, was passiert)
2. "subtext": Emotionaler Subtext / versteckte Bedeutung
3. "scene_goal": Was ist das Ziel/Konflikt dieser Szene?

Antworte NUR mit gültigem JSON, ohne Markdown oder Erklärungen.

Beispiel:
{{"summary": "Anna betritt ihre Wohnung...", "subtext": "Anna ist unsicher...", "scene_goal": "Anna sucht Unterstützung..."}}
"""
        else:
            return f"""Analyze this screenplay scene and return JSON:

{scene_info}

Create JSON response with:
1. "summary": Brief summary (1-2 sentences, what happens)
2. "subtext": Emotional subtext / hidden meaning
3. "scene_goal": What is the goal/conflict of this scene?

Respond ONLY with valid JSON, no markdown or explanations.

Example:
{{"summary": "Anna enters her apartment...", "subtext": "Anna is uncertain...", "scene_goal": "Anna seeks support..."}}
"""

    async def _call_openrouter(self, prompt: str) -> str:
        """Ruft OpenRouter API auf."""
        headers = {
            "Authorization": f"Bearer {self.settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/JohannesHoss/scene-analyzer",
        }

        payload = {
            "model": self.settings.openrouter_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,  # Konsistente Ergebnisse
        }

        response = await self.client.post(
            f"{self.settings.openrouter_base_url}/chat/completions",
            headers=headers,
            json=payload,
        )

        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def _parse_response(self, response: str) -> dict:
        """Parst KI-Response zu Dict."""
        try:
            # Entferne Markdown Code-Blocks falls vorhanden
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
                response = response.strip()

            data = json.loads(response)
            return {
                "summary": data.get("summary", ""),
                "subtext": data.get("subtext", ""),
                "scene_goal": data.get("scene_goal", ""),
            }
        except json.JSONDecodeError:
            # Fallback: Nimm ersten Satz
            return {
                "summary": response[:200],
                "subtext": "",
                "scene_goal": "",
            }

    def _extract_first_action(self, content: str) -> str:
        """Extrahiert erste Action-Beschreibung (Fallback ohne KI)."""
        lines = content.strip().split("\n")
        action_lines = []

        for line in lines:
            line = line.strip()
            # Skip leere Zeilen und Charakternamen (ALL CAPS)
            if not line or line.isupper():
                if action_lines:  # Wenn wir schon Action haben, stoppe
                    break
                continue
            action_lines.append(line)

        result = " ".join(action_lines)
        return result[:150] + "..." if len(result) > 150 else result

    async def close(self):
        """Schließt HTTP Client."""
        await self.client.aclose()
