from .base_parser import BaseParser


class TXTParser(BaseParser):
    """Parser for TXT files"""
    
    def extract_text(self) -> str:
        """Extract text from plain text file"""
        try:
            # Try UTF-8 first
            try:
                return self.content.decode('utf-8')
            except UnicodeDecodeError:
                # Fallback to Latin-1
                return self.content.decode('latin-1')
        
        except Exception as e:
            raise ValueError(f"Failed to parse TXT: {str(e)}")
