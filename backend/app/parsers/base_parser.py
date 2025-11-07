import re
from typing import List, Dict, Optional
from abc import ABC, abstractmethod


class BaseParser(ABC):
    """Base class for all document parsers"""
    
    def __init__(self, content: bytes):
        self.content = content
        self.text = ""
    
    @abstractmethod
    def extract_text(self) -> str:
        """Extract raw text from document"""
        pass
    
    def extract_scenes(self) -> List[Dict]:
        """Extract and parse scenes from text"""
        self.text = self.extract_text()
        
        # Try screenplay format first (with sluglines)
        scenes = self._extract_screenplay_scenes()
        
        # If no scenes found, try treatment format
        if len(scenes) == 0:
            scenes = self._extract_treatment_scenes()
        
        return scenes
    
    def _extract_screenplay_scenes(self) -> List[Dict]:
        """Extract scenes using slugline detection (INT./EXT.)"""
        scenes = []
        lines = self.text.split('\n')
        
        # Slugline patterns
        slugline_pattern = re.compile(
            r'^\s*(INT\.|EXT\.|INT/EXT\.)\s+(.+?)(?:\s*[-–—]\s*(.+?))?$',
            re.IGNORECASE
        )
        
        current_scene = None
        scene_number = 0
        
        for i, line in enumerate(lines):
            match = slugline_pattern.match(line.strip())
            
            if match:
                # Save previous scene
                if current_scene:
                    current_scene['text'] = current_scene['text'].strip()
                    current_scene['end_line'] = i - 1
                    scenes.append(current_scene)
                
                # Start new scene
                scene_number += 1
                current_scene = {
                    'number': scene_number,
                    'int_ext': match.group(1).upper(),
                    'location': match.group(2).strip() if match.group(2) else "UNKNOWN",
                    'time_of_day': match.group(3).strip().upper() if match.group(3) else "UNKNOWN",
                    'text': '',
                    'start_line': i
                }
            elif current_scene:
                # Add line to current scene
                current_scene['text'] += line + '\n'
        
        # Add last scene
        if current_scene:
            current_scene['text'] = current_scene['text'].strip()
            current_scene['end_line'] = len(lines)
            scenes.append(current_scene)
        
        return scenes
    
    def _extract_treatment_scenes(self) -> List[Dict]:
        """Extract scenes from treatment (without clear sluglines)"""
        scenes = []
        
        # Split by double line breaks or scene indicators
        paragraphs = re.split(r'\n\s*\n', self.text)
        
        # Time/location indicators that suggest new scene
        scene_indicators = [
            r'(?i)^später',
            r'(?i)^am nächsten tag',
            r'(?i)^währenddessen',
            r'(?i)^unterdessen',
            r'(?i)^in der',
            r'(?i)^im\s+\w+',
            r'(?i)^draussen',
            r'(?i)^drinnen',
        ]
        
        scene_number = 0
        current_text = []
        word_count = 0
        max_words_per_scene = 500
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # Check for scene indicators
            is_new_scene = any(re.match(pattern, para) for pattern in scene_indicators)
            para_words = len(para.split())
            
            # Start new scene if:
            # 1. Scene indicator found
            # 2. Word count exceeds threshold
            if is_new_scene or (word_count > max_words_per_scene and current_text):
                if current_text:
                    scene_number += 1
                    scenes.append({
                        'number': scene_number,
                        'int_ext': 'UNKNOWN',
                        'location': 'UNKNOWN',
                        'time_of_day': 'UNKNOWN',
                        'text': '\n\n'.join(current_text),
                        'start_line': None,
                        'end_line': None
                    })
                    current_text = []
                    word_count = 0
            
            current_text.append(para)
            word_count += para_words
        
        # Add last scene
        if current_text:
            scene_number += 1
            scenes.append({
                'number': scene_number,
                'int_ext': 'UNKNOWN',
                'location': 'UNKNOWN',
                'time_of_day': 'UNKNOWN',
                'text': '\n\n'.join(current_text),
                'start_line': None,
                'end_line': None
            })
        
        return scenes
    
    def detect_language(self) -> str:
        """Detect if text is German or English"""
        # Simple heuristic: count common German words
        german_indicators = ['der', 'die', 'das', 'und', 'ist', 'ich', 'Sie', 'nicht', 'von', 'mit']
        english_indicators = ['the', 'and', 'is', 'are', 'was', 'were', 'have', 'has', 'will', 'would']
        
        text_lower = self.text.lower()
        words = text_lower.split()
        
        german_count = sum(1 for word in words if word in german_indicators)
        english_count = sum(1 for word in words if word in english_indicators)
        
        return 'DE' if german_count > english_count else 'EN'
