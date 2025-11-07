from .pdf_parser import PDFParser
from .docx_parser import DOCXParser
from .txt_parser import TXTParser


def get_parser(file_type: str):
    """Factory function to get appropriate parser based on file type"""
    parsers = {
        ".pdf": PDFParser,
        ".docx": DOCXParser,
        ".txt": TXTParser
    }
    
    parser_class = parsers.get(file_type.lower())
    if not parser_class:
        raise ValueError(f"Unsupported file type: {file_type}")
    
    return parser_class


__all__ = ['PDFParser', 'DOCXParser', 'TXTParser', 'get_parser']
