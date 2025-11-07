from typing import List, Dict, Optional
import asyncio
from .openrouter_client import OpenRouterClient

# Aronson Analysis Questions
ARONSON_QUESTIONS_DE = [
    "Wer ist die Hauptfigur, und was will sie unbedingt?",
    "Welche Hindernisse stehen ihr im Weg?",
    "Was ist der Inciting Incident (auslösendes Ereignis)?",
    "Wie verschärfen sich die Konflikte im Mittelteil?",
    "Was ist der Climax – der Moment der Entscheidung?",
    "Wie verändert sich die Figur bis zum Ende?",
    "Gibt es eine durchgehende Action Line?",
    "Gibt es eine parallele Relationship Line?",
    "Wie ist die Balance zwischen Inner/Outer Story?",
    "Hat der Protagonist einen erkennbaren Makel (Flaw)?"
]

ARONSON_QUESTIONS_EN = [
    "Who is the protagonist and what do they absolutely want?",
    "What obstacles stand in their way?",
    "What is the inciting incident?",
    "How do conflicts intensify in the middle?",
    "What is the climax - the moment of decision?",
    "How does the character change by the end?",
    "Is there a continuous action line?",
    "Is there a parallel relationship line?",
    "What's the balance between inner/outer story?",
    "Does the protagonist have a recognizable flaw?"
]


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
                
                # Call AI with position context
                analysis = await asyncio.to_thread(
                    self.client.analyze_scene,
                    scene["text"],
                    self.mode,
                    self.language,
                    self.model,
                    scene_num + 1,  # scene_number (1-indexed)
                    total  # total_scenes
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
    
    async def analyze_story_structure(
        self,
        analysis_results: List[Dict]
    ) -> List[Dict]:
        """
        Analyze story structure for all scenes at once (Hero's Journey, Acts, Plot Points)
        
        Args:
            analysis_results: Already analyzed scene data (without story fields)
        
        Returns:
            Updated analysis_results with story structure fields added
        """
        total_scenes = len(analysis_results)
        
        # Create scene summaries
        scene_summaries = []
        for result in analysis_results:
            summary = (
                f"Scene {result.get('number', '?')}: "
                f"{result.get('location', 'UNKNOWN')} - "
                f"{result.get('story_event', 'No event')}"
            )
            scene_summaries.append(summary)
        
        context = "\n".join(scene_summaries)
        
        # Build prompt for story structure
        prompt_language = "German" if self.language == "DE" else "English"
        prompt = f"""You are analyzing the COMPLETE story structure of a {total_scenes}-scene screenplay.

All scenes summary:
{context}

Your task: Assign Hero's Journey stage, Act, and Plot Points to EACH scene based on the OVERALL story arc.

Guidelines:
- Hero's Journey should PROGRESS through stages (don't jump back and forth)
- Acts: 0-25% = Act I, 25-50% = Act II-A, 50-75% = Act II-B, 75-100% = Act III
- Major Plot Points occur only ONCE: Inciting Incident (~10%), Plot Point 1 (~25%), Midpoint (~50%), Plot Point 2 (~75%), Climax (~90%)
- Most scenes have plot_point_actual = "None"

Return JSON array with {total_scenes} objects in this format:
{{
  "scenes": [
    {{
      "scene_number": 1,
      "hero_journey": "Ordinary World",
      "act": "Act I",
      "plot_point_actual": "None",
      "plot_point_expected": "Setup"
    }},
    ...
  ]
}}

Hero's Journey options: Ordinary World, Call to Adventure, Crossing Threshold, Tests & Allies, Approach, Ordeal, Reward, Road Back, Resurrection, Return with Elixir, Not Applicable
Act options: Act I, Act II-A, Act II-B, Act III
Plot Point options: Inciting Incident, Plot Point 1, Midpoint, Plot Point 2, Climax, Resolution, None

Analyze in {prompt_language}. Return ONLY the JSON.
"""
        
        # Call AI
        try:
            response = await asyncio.to_thread(
                self.client.call_api,
                prompt,
                self.model,
                max_tokens=4000,
                temperature=0.2
            )
            
            # Parse response
            import json
            # Clean response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            response_data = json.loads(response)
            story_scenes = response_data.get("scenes", [])
            
            # Merge story data into analysis results
            for i, result in enumerate(analysis_results):
                if i < len(story_scenes):
                    story_data = story_scenes[i]
                    result["hero_journey"] = story_data.get("hero_journey", "Not Applicable")
                    result["act"] = story_data.get("act", "Act I")
                    result["plot_point_actual"] = story_data.get("plot_point_actual", "None")
                    result["plot_point_expected"] = story_data.get("plot_point_expected", "")
                else:
                    # Fallback if AI didn't return enough scenes
                    result["hero_journey"] = "Not Applicable"
                    result["act"] = "Act I"
                    result["plot_point_actual"] = "None"
                    result["plot_point_expected"] = ""
            
            return analysis_results
            
        except Exception as e:
            # Return with default story fields
            for result in analysis_results:
                result["hero_journey"] = "Not Applicable"
                result["act"] = "Act I"
                result["plot_point_actual"] = "None"
                result["plot_point_expected"] = f"Error: {str(e)}"
            return analysis_results
    
    async def analyze_aronson_questions(
        self,
        scenes: List[Dict],
        analysis_results: List[Dict]
    ) -> List[Dict[str, str]]:
        """
        Analyze screenplay using Aronson's 10 questions.
        
        Args:
            scenes: Original scene dictionaries with text
            analysis_results: Analyzed scene data
        
        Returns:
            List of dicts with 'question' and 'answer' keys
        """
        # Get questions based on language
        questions = ARONSON_QUESTIONS_DE if self.language == "DE" else ARONSON_QUESTIONS_EN
        
        # Create context summary from all scenes
        scene_summaries = []
        for i, result in enumerate(analysis_results[:30]):  # Limit to first 30 scenes for token efficiency
            summary = (
                f"Scene {result.get('number', i+1)}: "
                f"{result.get('location', 'UNKNOWN')} - "
                f"{result.get('story_event', 'No event')}"
            )
            scene_summaries.append(summary)
        
        context = "\n".join(scene_summaries)
        
        # Build prompt
        prompt_language = "German" if self.language == "DE" else "English"
        prompt = f"""You are analyzing a screenplay based on Linda Aronson's Single Path analysis method.

Here is a summary of the screenplay scenes:
{context}

Please answer the following {len(questions)} questions about the screenplay structure in {prompt_language}.
Provide detailed, insightful answers (2-4 sentences each).

Questions:
"""
        
        for i, question in enumerate(questions, 1):
            prompt += f"{i}. {question}\n"
        
        prompt += "\nProvide your answers in JSON format with this structure:\n"
        prompt += '{"answers": ["answer1", "answer2", ...]}'
        
        # Call AI
        try:
            response = await asyncio.to_thread(
                self.client.call_api,
                prompt,
                self.model,
                max_tokens=2000
            )
            
            # Parse response
            import json
            response_data = json.loads(response)
            answers = response_data.get("answers", [])
            
            # Combine questions and answers
            results = []
            for i, question in enumerate(questions):
                answer = answers[i] if i < len(answers) else "No answer provided"
                results.append({
                    "question": question,
                    "answer": answer
                })
            
            return results
            
        except Exception as e:
            # Return questions with error message
            return [
                {
                    "question": q,
                    "answer": f"Error during analysis: {str(e)}"
                }
                for q in questions
            ]
    
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
