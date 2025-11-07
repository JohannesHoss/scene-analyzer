import PyPDF2
import io
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
            
            return '\n'.join(text)
        
        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {str(e)}")
