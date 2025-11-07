import requests
import os
import json
from typing import Dict, Optional
import time


class OpenRouterClient:
    """Client for OpenRouter AI API"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"
        
        # Model mapping
        self.models = {
            "gpt-4o-mini": "openai/gpt-4o-mini",
            "gpt-4o": "openai/gpt-4o",
            "claude-3-haiku": "anthropic/claude-3-haiku",
            "gemini-flash": "google/gemini-1.5-flash",
            "llama-70b": "meta-llama/llama-3.1-70b-instruct"
        }
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")
    
    def analyze_scene(
        self, 
        scene_text: str, 
        mode: str, 
        language: str, 
        model: str,
        retry_count: int = 3
    ) -> Dict:
        """
        Analyze a single scene using AI
        
        Args:
            scene_text: The scene content
            mode: Analysis mode (standard, tatort, story, combined)
            language: Output language (DE or EN)
            model: Model identifier
            retry_count: Number of retries on failure
        
        Returns:
            Dict with analyzed scene data
        """
        model_id = self.models.get(model, self.models["gpt-4o-mini"])
        
        prompt = self._build_prompt(scene_text, mode, language)
        
        for attempt in range(retry_count):
            try:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://scene-analyzer.local",
                        "X-Title": "Scene Analyzer"
                    },
                    json={
                        "model": model_id,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a professional screenplay analyst. Analyze scenes accurately and return results in valid JSON format."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 1000
                    },
                    timeout=30
                )
                
                response.raise_for_status()
                result = response.json()
                
                # Extract content from response
                content = result['choices'][0]['message']['content']
                
                # Parse JSON from content
                parsed_data = self._parse_response(content, mode)
                
                return parsed_data
            
            except requests.exceptions.RequestException as e:
                if attempt == retry_count - 1:
                    raise Exception(f"API request failed after {retry_count} attempts: {str(e)}")
                time.sleep(2 ** attempt)  # Exponential backoff
            
            except (KeyError, json.JSONDecodeError) as e:
                if attempt == retry_count - 1:
                    raise Exception(f"Failed to parse API response: {str(e)}")
                time.sleep(1)
    
    def _build_prompt(self, scene: str, mode: str, language: str) -> str:
        """Build analysis prompt based on mode and language"""
        
        if language == "DE":
            base_prompt = f"""Analysiere diese Szene und gib die Informationen als JSON zurück.

SZENE:
{scene[:2000]}  

AUSGABE (als reines JSON, ohne Markdown):
{{
  "story_event": "Eine prägnante Zusammenfassung in einem Satz",
  "subtext": "Emotionale/unterschwellige Ebene in 5-10 Wörtern",
  "turning_point": "Action|Revelation|Decision|Realization|None",
  "on_stage": ["Charakter1", "Charakter2"],
  "off_stage": ["Erwähnter Charakter"],
  "protagonist_mood": "Wütend|Verzweifelt|Hoffnungsvoll|Erschöpft|Triumphierend|Verwirrt|Entschlossen"
}}"""
        else:  # EN
            base_prompt = f"""Analyze this scene and return the information as JSON.

SCENE:
{scene[:2000]}

OUTPUT (as pure JSON, no markdown):
{{
  "story_event": "A concise summary in one sentence",
  "subtext": "Emotional/subtext layer in 5-10 words",
  "turning_point": "Action|Revelation|Decision|Realization|None",
  "on_stage": ["Character1", "Character2"],
  "off_stage": ["Mentioned Character"],
  "protagonist_mood": "Angry|Desperate|Hopeful|Exhausted|Triumphant|Confused|Determined"
}}"""
        
        # Add mode-specific fields
        if mode in ["tatort", "combined"]:
            if language == "DE":
                base_prompt += """,
  "evidence": "Gefundene Beweismittel oder Spuren",
  "information_flow": "Wahrheit|Lüge|Teilgeständnis|Verschweigen|Irreführung",
  "knowledge_gap": "Zuschauer>Figur|Figur>Zuschauer|Gleichstand",
  "redundancy": "Neue Info|Wiederholung|Variation"
"""
            else:
                base_prompt += """,
  "evidence": "Found evidence or clues",
  "information_flow": "Truth|Lie|Partial confession|Concealment|Misdirection",
  "knowledge_gap": "Viewer>Character|Character>Viewer|Equal",
  "redundancy": "New info|Repetition|Variation"
"""
        
        if mode in ["story", "combined"]:
            base_prompt += """,
  "hero_journey": "Ordinary World|Call to Adventure|Crossing Threshold|Tests & Allies|Approach|Ordeal|Reward|Road Back|Resurrection|Return with Elixir|Not Applicable",
  "act": "Act I|Act II-A|Act II-B|Act III",
  "plot_point_actual": "Inciting Incident|Plot Point 1|Midpoint|Plot Point 2|Climax|Resolution|None",
  "plot_point_expected": "Expected plot point based on position"
"""
        
        base_prompt += "\n}\n\nWichtig: Antworte NUR mit dem JSON-Objekt, ohne zusätzlichen Text oder Markdown-Formatierung."
        
        return base_prompt
    
    def _parse_response(self, content: str, mode: str) -> Dict:
        """Parse AI response and extract JSON"""
        
        # Remove markdown code blocks if present
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from text
            import re
            json_match = re.search(r'\{[^}]+\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                raise ValueError(f"Could not parse JSON from response: {content[:200]}")
        
        # Validate required fields
        required_fields = ["story_event", "subtext", "turning_point", "on_stage", "protagonist_mood"]
        for field in required_fields:
            if field not in data:
                data[field] = "Unknown"
        
        # Ensure lists
        if not isinstance(data.get("on_stage"), list):
            data["on_stage"] = []
        if not isinstance(data.get("off_stage"), list):
            data["off_stage"] = []
        
        return data
