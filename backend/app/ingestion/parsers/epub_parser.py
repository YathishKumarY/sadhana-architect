import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

from app.ingestion.parsers.base import BaseParser, ParsedPage


class EPUBParser(BaseParser):
    def supports(self, file_path: str) -> bool:
        return file_path.lower().endswith(".epub")

    def parse(self, file_path: str) -> list[ParsedPage]:
        pages = []
        book = epub.read_epub(file_path)

        page_num = 0
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            content = item.get_content().decode("utf-8", errors="ignore")
            soup = BeautifulSoup(content, "html.parser")
            text = soup.get_text(separator="\n").strip()

            if text and len(text) > 50:
                page_num += 1
                has_verses = self._detect_verse_markers(text)
                pages.append(ParsedPage(
                    page_number=page_num,
                    text=text,
                    has_verse_markers=has_verses,
                ))

        return pages

    def _detect_verse_markers(self, text: str) -> bool:
        import re
        verse_patterns = [
            r"^\s*\d+\.\d+",
            r"^\s*Verse\s+\d+",
            r"^\s*Sutra\s+\d+",
            r"^\s*\d+\s*[-–]\s",
        ]
        for pattern in verse_patterns:
            if re.search(pattern, text, re.MULTILINE):
                return True
        return False
