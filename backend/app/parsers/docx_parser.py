import docx
import io
from .base_parser import BaseParser


class DOCXParser(BaseParser):
    """Parser for DOCX files"""
    
    def extract_text(self) -> str:
        """Extract text from DOCX using python-docx"""
        try:
            docx_file = io.BytesIO(self.content)
            doc = docx.Document(docx_file)
            
            text = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text.append(paragraph.text)
            
            return '\n'.join(text)
        
        except Exception as e:
            raise ValueError(f"Failed to parse DOCX: {str(e)}")
