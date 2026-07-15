from abc import ABC, abstractmethod


class BaseParser(ABC):
    """Abstract base class for resume parsers."""

    @abstractmethod
    def parse(self, file_path: str) -> str:
        """Parse a resume file and extract raw text."""
        pass

    def validate_file(self, file_path: str):
        """Validate that the file exists and is readable."""
        import os
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        if not os.path.isfile(file_path):
            raise ValueError(f"Not a file: {file_path}")
