import os
from datetime import datetime

from app.ingestion.parsers.pdf_parser import PDFParser
from app.ingestion.parsers.epub_parser import EPUBParser
from app.ingestion.chunkers.verse_chunker import VerseChunker
from app.ingestion.chunkers.chapter_chunker import ChapterChunker
from app.ingestion.chunkers.commentary_chunker import CommentaryChunker
from app.ingestion.chunkers.base import Chunk
from app.core.embeddings import embedding_service
from app.db.vector_store import vector_store


class IngestionPipeline:
    def __init__(self):
        self.pdf_parser = PDFParser()
        self.epub_parser = EPUBParser()
        self.verse_chunker = VerseChunker()
        self.chapter_chunker = ChapterChunker()
        self.commentary_chunker = CommentaryChunker()

    def _get_parser(self, file_path: str):
        if self.pdf_parser.supports(file_path):
            return self.pdf_parser
        if self.epub_parser.supports(file_path):
            return self.epub_parser
        raise ValueError(f"No parser available for: {file_path}")

    def _select_chunker(self, full_text: str, metadata: dict):
        """Select the best chunker based on text structure analysis."""
        has_labeled_commentary = any(
            label in full_text
            for label in ["Commentary:", "Explanation:", "Bhashya:", "Meaning:"]
        )
        if has_labeled_commentary:
            return self.commentary_chunker

        import re
        verse_pattern_count = len(re.findall(r"^\s*\d+\.\d+", full_text, re.MULTILINE))
        if verse_pattern_count >= 3:
            return self.verse_chunker

        verse_keyword_count = len(re.findall(r"^(?:Verse|Sutra)\s+\d+", full_text, re.MULTILINE))
        if verse_keyword_count >= 3:
            return self.verse_chunker

        return self.chapter_chunker

    async def ingest(
        self,
        file_path: str,
        title: str,
        author: str | None = None,
        tradition: str | None = None,
    ) -> dict:
        """Full ingestion pipeline: parse, chunk, embed, store."""
        parser = self._get_parser(file_path)
        pages = parser.parse(file_path)

        full_text = "\n\n".join(page.text for page in pages)

        source_metadata = {
            "source_book": title,
            "author": author or "Unknown",
            "tradition": tradition or "general",
            "file_path": os.path.basename(file_path),
        }

        chunker = self._select_chunker(full_text, source_metadata)
        chunks = chunker.chunk(full_text, source_metadata)

        if not chunks:
            return {"status": "error", "message": "No chunks produced", "total_chunks": 0}

        batch_size = 10
        total_stored = 0

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            texts = [c.text for c in batch]
            embeddings = await embedding_service.embed_batch(texts)

            ids = [c.id for c in batch]
            metadatas = [c.metadata for c in batch]

            technique_chunks = [(j, c) for j, c in enumerate(batch) if c.is_technique]
            general_chunks = [(j, c) for j, c in enumerate(batch) if not c.is_technique]

            if general_chunks:
                gen_indices = [j for j, _ in general_chunks]
                vector_store.add_chunks(
                    ids=[ids[j] for j in gen_indices],
                    documents=[texts[j] for j in gen_indices],
                    embeddings=[embeddings[j] for j in gen_indices],
                    metadatas=[metadatas[j] for j in gen_indices],
                    is_technique=False,
                )

            if technique_chunks:
                tech_indices = [j for j, _ in technique_chunks]
                vector_store.add_chunks(
                    ids=[ids[j] for j in tech_indices],
                    documents=[texts[j] for j in tech_indices],
                    embeddings=[embeddings[j] for j in tech_indices],
                    metadatas=[metadatas[j] for j in tech_indices],
                    is_technique=True,
                )

            # Also store techniques in the general collection for broader queries
            if technique_chunks:
                tech_indices = [j for j, _ in technique_chunks]
                vector_store.add_chunks(
                    ids=[f"{ids[j]}__general" for j in tech_indices],
                    documents=[texts[j] for j in tech_indices],
                    embeddings=[embeddings[j] for j in tech_indices],
                    metadatas=[metadatas[j] for j in tech_indices],
                    is_technique=False,
                )

            total_stored += len(batch)

        return {
            "status": "completed",
            "total_chunks": total_stored,
            "techniques_count": sum(1 for c in chunks if c.is_technique),
            "philosophy_count": sum(1 for c in chunks if not c.is_technique),
            "chunker_used": chunker.__class__.__name__,
            "ingested_at": datetime.utcnow().isoformat(),
        }


ingestion_pipeline = IngestionPipeline()
