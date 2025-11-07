import PyPDF2
import io
import re
from .base_parser import BaseParser


class PDFParser(BaseParser):
    """Parser for PDF files"""
    
    def extract_text(self) -> str:
        """Extract text from PDF using PyPDF2"""
        try:
            pdf_file = io.BytesIO(self.content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = []
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
            
            raw_text = '\n'.join(text)
            
            # Fix screenplay PDFs: Add line breaks before sluglines that are in the middle of lines
            # Step 1: Handle sluglines after sentence endings
            slugline_pattern = r'([.!?])\s+(INT\.|EXT\.|INT/EXT\.)\s+'
            raw_text = re.sub(slugline_pattern, r'\1\n\n\2 ', raw_text, flags=re.IGNORECASE)
            
            # Step 2: Handle "DAY" or "NIGHT" followed immediately by next slugline
            day_night_pattern = r'(DAY|NIGHT|MORNING|AFTERNOON|EVENING)\s+(INT\.|EXT\.|INT/EXT\.)\s+'
            raw_text = re.sub(day_night_pattern, r'\1\n\n\2 ', raw_text, flags=re.IGNORECASE)
            
            # Step 3: Handle uppercase text that appears right after DAY/NIGHT in sluglines
            # e.g. "- DAYEarly morning" -> "- DAY\nEarly morning"
            # e.g. "- DAYTHE sound" -> "- DAY\nThe sound"
            day_text_pattern = r'(-\s*(?:DAY|NIGHT|MORNING|AFTERNOON|EVENING))([A-Z][a-z])'
            raw_text = re.sub(day_text_pattern, r'\1\n\2', raw_text, flags=re.IGNORECASE)
            
            # Step 4: Handle sluglines that appear after uppercase words (common in PDFs)
            uppercase_slugline_pattern = r'([A-Z]{3,})(INT\.|EXT\.|INT/EXT\.)\s+'
            raw_text = re.sub(uppercase_slugline_pattern, r'\1\n\n\2 ', raw_text, flags=re.IGNORECASE)
            
            return raw_text
        
        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {str(e)}")
