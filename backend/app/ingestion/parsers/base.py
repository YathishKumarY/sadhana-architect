from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ParsedPage:
    page_number: int
    text: str
    has_verse_markers: bool = False


class BaseParser(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> list[ParsedPage]:
        """Parse a file and return list of pages with text content."""
        ...

    @abstractmethod
    def supports(self, file_path: str) -> bool:
        """Check if this parser supports the given file type."""
        ...
