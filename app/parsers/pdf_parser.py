from PyPDF2 import PdfReader
from app.parsers.base_parser import BaseParser


class PDFParser(BaseParser):
    """Parser for PDF resume files."""

    def parse(self, file_path: str) -> str:
        """Extract text from a PDF file."""
        self.validate_file(file_path)

        reader = PdfReader(file_path)
        text_parts = []

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

        return "\n".join(text_parts)
