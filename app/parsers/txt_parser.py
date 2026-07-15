from app.parsers.base_parser import BaseParser


class TXTParser(BaseParser):
    """Parser for plain text resume files."""

    def parse(self, file_path: str) -> str:
        """Extract text from a TXT file."""
        self.validate_file(file_path)

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
