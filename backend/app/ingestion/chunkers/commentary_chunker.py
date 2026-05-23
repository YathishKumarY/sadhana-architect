import re

from app.ingestion.chunkers.base import BaseChunker, Chunk


class CommentaryChunker(BaseChunker):
    """Chunks texts that have sutras/verses with nested commentaries.

    Handles the pattern: short sutra text followed by longer commentary,
    keeping them bundled as a single unit.
    """

    SUTRA_COMMENTARY_PATTERNS = [
        (r"^(Sutra\s+\d+[:\.]?\s*.+?)(?=^Commentary|^Explanation|^Meaning|^Bhashya)", "sutra_then_label"),
        (r"^(\d+\.\d+)\s+(.+?)(\n\s*\n)(.+?)(?=^\d+\.\d+|\Z)", "numbered_with_gap"),
    ]

    def chunk(self, full_text: str, source_metadata: dict) -> list[Chunk]:
        chunks = self._try_labeled_commentary(full_text, source_metadata)
        if chunks:
            return chunks

        chunks = self._try_sutra_gap_commentary(full_text, source_metadata)
        if chunks:
            return chunks

        return self._simple_sutra_commentary(full_text, source_metadata)

    def _try_labeled_commentary(self, text: str, source_metadata: dict) -> list[Chunk]:
        """Handle texts where commentary is explicitly labeled."""
        commentary_labels = r"(?:Commentary|Explanation|Meaning|Bhashya|Notes?)[:\.]?"
        pattern = (
            r"(?:^|\n)(?:Sutra|Verse|Aphorism)\s+(\d+)[:\.]?\s*"
            r"(.+?)"
            r"(?:^|\n)" + commentary_labels + r"\s*"
            r"(.+?)"
            r"(?=(?:^|\n)(?:Sutra|Verse|Aphorism)\s+\d+|\Z)"
        )

        matches = list(re.finditer(pattern, text, re.MULTILINE | re.DOTALL))
        if len(matches) < 2:
            return []

        chunks = []
        book_slug = source_metadata.get("source_book", "unknown").lower().replace(" ", "-")

        for match in matches:
            sutra_num = int(match.group(1))
            sutra_text = match.group(2).strip()
            commentary_text = match.group(3).strip()

            combined = f"Sutra {sutra_num}: {sutra_text}\n\nCommentary: {commentary_text}"
            category = self._classify_practice_category(combined)

            chunk_id = f"{book_slug}__sutra{sutra_num}__with_commentary"
            chunks.append(Chunk(
                id=chunk_id,
                text=combined,
                metadata={
                    **source_metadata,
                    "verse_num": sutra_num,
                    "chunk_type": "sutra_with_commentary",
                    "has_commentary": True,
                    "practice_category": category,
                },
            ))

        return chunks

    def _try_sutra_gap_commentary(self, text: str, source_metadata: dict) -> list[Chunk]:
        """Handle numbered sutras followed by explanatory paragraphs."""
        pattern = r"^(\d+)\.(\d+)\s+(.+?)(?:\n\s*\n)(.+?)(?=^\d+\.\d+|\Z)"
        matches = list(re.finditer(pattern, text, re.MULTILINE | re.DOTALL))

        if len(matches) < 2:
            return []

        chunks = []
        book_slug = source_metadata.get("source_book", "unknown").lower().replace(" ", "-")

        for match in matches:
            chapter = int(match.group(1))
            verse = int(match.group(2))
            sutra_text = match.group(3).strip()
            commentary = match.group(4).strip()

            combined = f"{chapter}.{verse} {sutra_text}\n\n{commentary}"
            category = self._classify_practice_category(combined)

            chunk_id = f"{book_slug}__ch{chapter}__v{verse}__commented"
            chunks.append(Chunk(
                id=chunk_id,
                text=combined,
                metadata={
                    **source_metadata,
                    "chapter_num": chapter,
                    "verse_num": verse,
                    "chunk_type": "verse_with_commentary",
                    "has_commentary": True,
                    "practice_category": category,
                },
            ))

        return chunks

    def _simple_sutra_commentary(self, text: str, source_metadata: dict) -> list[Chunk]:
        """Fallback: split on double newlines and pair short+long blocks."""
        blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
        chunks = []
        book_slug = source_metadata.get("source_book", "unknown").lower().replace(" ", "-")

        i = 0
        chunk_num = 0
        while i < len(blocks):
            block = blocks[i]
            chunk_num += 1

            if len(block) < 200 and i + 1 < len(blocks) and len(blocks[i + 1]) > len(block):
                combined = f"{block}\n\n{blocks[i + 1]}"
                i += 2
            else:
                combined = block
                i += 1

            if len(combined) < 50:
                continue

            category = self._classify_practice_category(combined)
            chunk_id = f"{book_slug}__block{chunk_num}"
            chunks.append(Chunk(
                id=chunk_id,
                text=combined,
                metadata={
                    **source_metadata,
                    "chunk_type": "commentary_block",
                    "block_num": chunk_num,
                    "practice_category": category,
                },
            ))

        return chunks
