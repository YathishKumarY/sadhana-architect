import fitz

from app.ingestion.parsers.base import BaseParser, ParsedPage


class PDFParser(BaseParser):
    def supports(self, file_path: str) -> bool:
        return file_path.lower().endswith(".pdf")

    def parse(self, file_path: str) -> list[ParsedPage]:
        pages = []
        doc = fitz.open(file_path)

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")

            if text.strip():
                has_verses = self._detect_verse_markers(text)
                pages.append(ParsedPage(
                    page_number=page_num + 1,
                    text=text.strip(),
                    has_verse_markers=has_verses,
                ))

        doc.close()
        return pages

    def _detect_verse_markers(self, text: str) -> bool:
        import re
        verse_patterns = [
            r"^\s*\d+\.\d+",
            r"^\s*Verse\s+\d+",
            r"^\s*Sutra\s+\d+",
            r"॥\s*\d+\s*॥",
            r"^\s*\d+\s*[-–]\s",
            r"^\s*[IVX]+\.\d+",
        ]
        for pattern in verse_patterns:
            if re.search(pattern, text, re.MULTILINE):
                return True
        return False
