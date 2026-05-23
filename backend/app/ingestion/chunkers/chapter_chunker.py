import re

from app.ingestion.chunkers.base import BaseChunker, Chunk


class ChapterChunker(BaseChunker):
    """Chunks prose texts by chapter/section headings with sliding window fallback.

    Used for dense commentary texts that don't have verse-level structure.
    """

    HEADING_PATTERNS = [
        r"^Chapter\s+(\d+|[IVXLC]+)[:\.]?\s*(.*)",
        r"^CHAPTER\s+(\d+|[IVXLC]+)[:\.]?\s*(.*)",
        r"^Section\s+(\d+)[:\.]?\s*(.*)",
        r"^Part\s+(\d+|[IVXLC]+)[:\.]?\s*(.*)",
        r"^#{1,3}\s+(.+)",
    ]

    MAX_CHUNK_TOKENS = 512
    OVERLAP_TOKENS = 64

    def chunk(self, full_text: str, source_metadata: dict) -> list[Chunk]:
        sections = self._split_by_headings(full_text)

        if len(sections) <= 1:
            return self._sliding_window_chunk(full_text, source_metadata)

        chunks = []
        book_slug = source_metadata.get("source_book", "unknown").lower().replace(" ", "-")

        for i, (heading, content) in enumerate(sections):
            if len(content.strip()) < 50:
                continue

            if self._estimate_tokens(content) > self.MAX_CHUNK_TOKENS:
                sub_chunks = self._sliding_window_chunk(
                    content,
                    {**source_metadata, "section": heading or f"section_{i+1}"},
                )
                chunks.extend(sub_chunks)
            else:
                category = self._classify_practice_category(content)
                chunk_id = f"{book_slug}__sec{i+1}"
                chunks.append(Chunk(
                    id=chunk_id,
                    text=content.strip(),
                    metadata={
                        **source_metadata,
                        "section": heading or f"section_{i+1}",
                        "chunk_type": "section",
                        "practice_category": category,
                    },
                ))

        return chunks

    def _split_by_headings(self, text: str) -> list[tuple[str | None, str]]:
        combined_pattern = "|".join(f"({p})" for p in self.HEADING_PATTERNS)
        splits = re.split(f"({combined_pattern})", text, flags=re.MULTILINE)

        sections = []
        current_heading = None
        current_content = []

        for part in splits:
            if part is None:
                continue
            is_heading = any(re.match(p, part.strip(), re.MULTILINE) for p in self.HEADING_PATTERNS)
            if is_heading:
                if current_content:
                    sections.append((current_heading, "\n".join(current_content)))
                current_heading = part.strip()
                current_content = []
            else:
                current_content.append(part)

        if current_content:
            sections.append((current_heading, "\n".join(current_content)))

        return sections

    def _sliding_window_chunk(self, text: str, source_metadata: dict) -> list[Chunk]:
        words = text.split()
        chunks = []
        book_slug = source_metadata.get("source_book", "unknown").lower().replace(" ", "-")
        section = source_metadata.get("section", "main")

        start = 0
        chunk_num = 0
        while start < len(words):
            end = min(start + self.MAX_CHUNK_TOKENS, len(words))
            chunk_text = " ".join(words[start:end])

            if len(chunk_text.strip()) >= 50:
                chunk_num += 1
                category = self._classify_practice_category(chunk_text)
                chunk_id = f"{book_slug}__{section}__win{chunk_num}"
                chunks.append(Chunk(
                    id=chunk_id,
                    text=chunk_text,
                    metadata={
                        **source_metadata,
                        "chunk_type": "window",
                        "window_num": chunk_num,
                        "practice_category": category,
                    },
                ))

            start = end - self.OVERLAP_TOKENS
            if start >= len(words):
                break

        return chunks

    def _estimate_tokens(self, text: str) -> int:
        return len(text.split())
