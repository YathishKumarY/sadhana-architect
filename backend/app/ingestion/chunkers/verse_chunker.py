import re

from app.ingestion.chunkers.base import BaseChunker, Chunk


class VerseChunker(BaseChunker):
    """Chunks text by verse/sutra boundaries.

    Handles: Yoga Sutras, Bhagavad Gita, Hatha Yoga Pradipika,
    Vijnana Bhairava Tantra, and similar verse-structured texts.
    """

    VERSE_PATTERNS = [
        (r"^(\d+)\.(\d+)\s+(.+?)(?=^\d+\.\d+|\Z)", "chapter_dot_verse"),
        (r"^Verse\s+(\d+)[:\.]?\s*(.+?)(?=^Verse\s+\d+|\Z)", "verse_keyword"),
        (r"^Sutra\s+(\d+)[:\.]?\s*(.+?)(?=^Sutra\s+\d+|\Z)", "sutra_keyword"),
        (r"^\s*(\d+)\s*[-–.]\s+(.+?)(?=^\s*\d+\s*[-–.]|\Z)", "numbered_dash"),
        (r"॥\s*(\d+)\s*॥\s*(.+?)(?=॥\s*\d+\s*॥|\Z)", "devanagari"),
    ]

    def chunk(self, full_text: str, source_metadata: dict) -> list[Chunk]:
        chunks = []

        for pattern, pattern_type in self.VERSE_PATTERNS:
            matches = list(re.finditer(pattern, full_text, re.MULTILINE | re.DOTALL))
            if len(matches) >= 3:
                chunks = self._extract_chunks(matches, pattern_type, source_metadata)
                break

        if not chunks:
            chunks = self._fallback_paragraph_chunk(full_text, source_metadata)

        return chunks

    def _extract_chunks(self, matches: list, pattern_type: str, source_metadata: dict) -> list[Chunk]:
        chunks = []
        book_slug = source_metadata.get("source_book", "unknown").lower().replace(" ", "-")

        for match in matches:
            groups = match.groups()

            if pattern_type == "chapter_dot_verse":
                chapter_num = int(groups[0])
                verse_num = int(groups[1])
                text = groups[2].strip()
                chunk_id = f"{book_slug}__ch{chapter_num}__v{verse_num}"
            elif pattern_type in ("verse_keyword", "sutra_keyword", "numbered_dash"):
                verse_num = int(groups[0])
                text = groups[1].strip()
                chapter_num = source_metadata.get("chapter_num")
                chunk_id = f"{book_slug}__v{verse_num}"
            elif pattern_type == "devanagari":
                verse_num = int(groups[0])
                text = groups[1].strip()
                chapter_num = source_metadata.get("chapter_num")
                chunk_id = f"{book_slug}__v{verse_num}"
            else:
                continue

            if len(text) < 20:
                continue

            category = self._classify_practice_category(text)

            metadata = {
                **source_metadata,
                "verse_num": verse_num,
                "chunk_type": "verse",
                "practice_category": category,
            }
            if chapter_num is not None:
                metadata["chapter_num"] = chapter_num

            chunks.append(Chunk(id=chunk_id, text=text, metadata=metadata))

        return chunks

    def _fallback_paragraph_chunk(self, text: str, source_metadata: dict) -> list[Chunk]:
        """Fallback: split by double newlines when no verse pattern detected."""
        paragraphs = re.split(r"\n\s*\n", text)
        chunks = []
        book_slug = source_metadata.get("source_book", "unknown").lower().replace(" ", "-")

        for i, para in enumerate(paragraphs):
            para = para.strip()
            if len(para) < 50:
                continue

            category = self._classify_practice_category(para)
            chunk_id = f"{book_slug}__para{i+1}"

            chunks.append(Chunk(
                id=chunk_id,
                text=para,
                metadata={
                    **source_metadata,
                    "chunk_type": "paragraph",
                    "paragraph_num": i + 1,
                    "practice_category": category,
                },
            ))

        return chunks
