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
                parsed_data = self._parse_response(content, mode, language)
                
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
  "location": "Konkreter Schauplatz aus dem Text (z.B. 'Wohnzimmer', 'Polizeirevier', 'Park')",
  "time_of_day": "Tageszeit aus dem Kontext (z.B. 'Morgen', 'Nachmittag', 'Nacht', 'Unbekannt')",
  "int_ext": "INT|EXT|UNBEKANNT (Innenraum oder Außenbereich)",
  "story_event": "Eine prägnante Zusammenfassung in einem Satz - WAS passiert?",
  "subtext": "Emotionale/unterschwellige Ebene in 5-10 Wörtern - was wird NICHT gesagt?",
  "turning_point_type": "Action|Revelation|Decision|Realization|None",
  "turning_point_moment": "Der genaue Moment/Satz wo der Wendepunkt passiert (z.B. 'Als sie die Tür öffnet und die Leiche sieht') oder 'Keiner'",
  "on_stage": ["Charakter1", "Charakter2"],
  "off_stage": ["Erwähnter aber nicht anwesender Charakter"],
  "protagonist_mood": "Stimmung des Hauptcharakters (Wütend|Verzweifelt|Hoffnungsvoll|Erschöpft|Triumphierend|Verwirrt|Entschlossen|Neutral)"
}}"""
        else:  # EN
            base_prompt = f"""Analyze this scene and return the information as JSON.

SCENE:
{scene[:2000]}

OUTPUT (as pure JSON, no markdown):
{{
  "location": "Specific location from context (e.g. 'Living room', 'Police station', 'Park')",
  "time_of_day": "Time from context (e.g. 'Morning', 'Afternoon', 'Night', 'Unknown')",
  "int_ext": "INT|EXT|UNKNOWN (Interior or Exterior)",
  "story_event": "A concise summary in one sentence - WHAT happens?",
  "subtext": "Emotional/subtext layer in 5-10 words - what is NOT said?",
  "turning_point_type": "Action|Revelation|Decision|Realization|None",
  "turning_point_moment": "The exact moment/sentence where the turning point happens (e.g. 'When she opens the door and sees the body') or 'None'",
  "on_stage": ["Character1", "Character2"],
  "off_stage": ["Mentioned but not present character"],
  "protagonist_mood": "Main character's mood (Angry|Desperate|Hopeful|Exhausted|Triumphant|Confused|Determined|Neutral)"
}}"""
        
        # Add mode-specific fields
        if mode in ["tatort", "combined"]:
            if language == "DE":
                base_prompt += """,
  "evidence": "Gefundene Beweismittel, Spuren oder wichtige Objekte (oder 'Keine')",
  "information_flow": "Wahrheit (sagt die Wahrheit)|Lüge (lügt aktiv)|Teilgeständnis (halb wahr)|Verschweigen (lässt Info weg)|Irreführung (lenkt ab)",
  "knowledge_gap": "Zuschauer weiß mehr als Figur|Figur weiß mehr als Zuschauer|Beide wissen gleich viel",
  "redundancy": "Neue Info (erste Erwähnung)|Wiederholung (exakt gleich)|Variation (neue Perspektive auf bekannte Info)",
  "suspect_status": "Liste von Charakteren mit Status: 'Name (Verdächtig - Grund)'|'Name (Alibi - Details)'|'Name (Neutral)' oder 'Keine Verdächtigen in dieser Szene'"
"""
            else:
                base_prompt += """,
  "evidence": "Found evidence, clues or important objects (or 'None')",
  "information_flow": "Truth (tells truth)|Lie (actively lies)|Partial confession (half true)|Concealment (withholds info)|Misdirection (deflects)",
  "knowledge_gap": "Viewer knows more than character|Character knows more than viewer|Both know equally",
  "redundancy": "New info (first mention)|Repetition (exactly same)|Variation (new perspective on known info)",
  "suspect_status": "List of characters with status: 'Name (Suspect - reason)'|'Name (Alibi - details)'|'Name (Neutral)' or 'No suspects in this scene'"
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
    
    def _parse_response(self, content: str, mode: str, language: str) -> Dict:
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
        required_fields = ["story_event", "subtext", "on_stage", "protagonist_mood"]
        for field in required_fields:
            if field not in data:
                data[field] = "Unknown"
        
        # Handle turning point (backward compatibility)
        if "turning_point_type" not in data:
            # Try old format first
            if "turning_point" in data:
                data["turning_point_type"] = data["turning_point"]
            else:
                data["turning_point_type"] = "None"
        
        if "turning_point_moment" not in data:
            data["turning_point_moment"] = "Keiner" if language == "DE" else "None"
        
        # Ensure lists
        if not isinstance(data.get("on_stage"), list):
            data["on_stage"] = []
        if not isinstance(data.get("off_stage"), list):
            data["off_stage"] = []
        
        return data
