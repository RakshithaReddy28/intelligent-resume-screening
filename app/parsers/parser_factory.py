from app.parsers.pdf_parser import PDFParser
from app.parsers.docx_parser import DOCXParser
from app.parsers.txt_parser import TXTParser
from app.parsers.base_parser import BaseParser


class ParserFactory:
    """Factory for creating resume parsers based on file type."""

    _parsers = {
        "pdf": PDFParser,
        "docx": DOCXParser,
        "txt": TXTParser,
    }

    @classmethod
    def get_parser(cls, file_type: str) -> BaseParser:
        """Get the appropriate parser for a file type."""
        parser_class = cls._parsers.get(file_type.lower())
        if not parser_class:
            raise ValueError(f"Unsupported file type: {file_type}")
        return parser_class()

    @classmethod
    def supported_types(cls) -> list:
        """Return list of supported file types."""
        return list(cls._parsers.keys())
