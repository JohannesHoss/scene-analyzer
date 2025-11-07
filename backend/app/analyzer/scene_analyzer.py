from typing import List, Dict
import asyncio
from .openrouter_client import OpenRouterClient


class SceneAnalyzer:
    """Analyzes scenes using AI with token optimization"""
    
    def __init__(self, client: OpenRouterClient, mode: str, language: str, model: str):
        self.client = client
        self.mode = mode
        self.language = language
        self.model = model
    
    async def analyze_all_scenes(
        self, 
        scenes: List[Dict], 
        job_storage: Dict,
        job_id: str
    ) -> List[Dict]:
        """
        Analyze all scenes with progress updates
        
        Args:
            scenes: List of scene dictionaries
            job_storage: Reference to job storage for progress updates
            job_id: Job identifier
        
        Returns:
            List of analyzed scene data
        """
        total = len(scenes)
        results = []
        
        # Always analyze ALL scenes
        scenes_to_analyze = list(enumerate(scenes))
        
        # Update job status
        job_storage[job_id]["status"] = "analyzing"
        job_storage[job_id]["total_scenes"] = len(scenes_to_analyze)
        
        # Analyze ALL scenes
        for idx, (scene_num, scene) in enumerate(scenes_to_analyze):
            try:
                # Update progress
                job_storage[job_id]["current_scene"] = idx + 1
                job_storage[job_id]["progress"] = int((idx + 1) / len(scenes_to_analyze) * 100)
                
                # Call AI
                analysis = await asyncio.to_thread(
                    self.client.analyze_scene,
                    scene["text"],
                    self.mode,
                    self.language,
                    self.model
                )
                
                # Merge with scene metadata
                # AI values override regex-detected values
                result = {
                    "number": scene_num + 1,
                    "int_ext": analysis.get("int_ext", scene.get("int_ext", "UNKNOWN")),
                    "location": analysis.get("location", scene.get("location", "UNKNOWN")),
                    "time_of_day": analysis.get("time_of_day", scene.get("time_of_day", "UNKNOWN")),
                    **analysis
                }
                
                results.append(result)
                
            except Exception as e:
                # Add error entry for this scene
                results.append({
                    "number": scene_num + 1,
                    "int_ext": scene.get("int_ext", "UNKNOWN"),
                    "location": scene.get("location", "UNKNOWN"),
                    "time_of_day": scene.get("time_of_day", "UNKNOWN"),
                    "story_event": f"Error: {str(e)}",
                    "subtext": "Analysis failed",
                    "turning_point": "None",
                    "on_stage": [],
                    "off_stage": [],
                    "protagonist_mood": "Unknown"
                })
        
        return results
    
    def estimate_cost(self, scene_count: int) -> float:
        """
        Estimate analysis cost in EUR
        
        Rough estimates based on average tokens per scene:
        - Input: ~500 tokens per scene
        - Output: ~200 tokens per scene
        - gpt-4o-mini: ~$0.15 per 1M input, ~$0.60 per 1M output
        """
        # Analyze ALL scenes
        actual_scenes = scene_count
        
        # Token estimates
        input_tokens = actual_scenes * 500
        output_tokens = actual_scenes * 200
        
        # Cost per model (USD)
        costs = {
            "gpt-4o-mini": (input_tokens * 0.15 / 1_000_000) + (output_tokens * 0.60 / 1_000_000),
            "gpt-4o": (input_tokens * 2.50 / 1_000_000) + (output_tokens * 10.00 / 1_000_000),
            "claude-3-haiku": (input_tokens * 0.25 / 1_000_000) + (output_tokens * 1.25 / 1_000_000),
            "gemini-flash": (input_tokens * 0.075 / 1_000_000) + (output_tokens * 0.30 / 1_000_000),
            "llama-70b": (input_tokens * 0.18 / 1_000_000) + (output_tokens * 0.18 / 1_000_000)
        }
        
        cost_usd = costs.get(self.model, costs["gpt-4o-mini"])
        cost_eur = cost_usd * 1.08  # Rough USD to EUR conversion
        
        return round(cost_eur, 3)
