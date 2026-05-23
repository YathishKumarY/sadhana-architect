"""Bulk ingest all texts from the backend/texts/ directory."""
import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.ingestion.pipeline import ingestion_pipeline


TEXTS_DIR = os.path.join(os.path.dirname(__file__), "..", "backend", "texts")


async def main():
    files = [
        f for f in os.listdir(TEXTS_DIR)
        if f.endswith((".pdf", ".epub")) and not f.startswith(".")
    ]

    if not files:
        print(f"No PDF or EPUB files found in {TEXTS_DIR}")
        print("Place your spiritual texts there and run this script again.")
        return

    print(f"Found {len(files)} text(s) to ingest:\n")

    for filename in sorted(files):
        file_path = os.path.join(TEXTS_DIR, filename)
        title = os.path.splitext(filename)[0].replace("-", " ").replace("_", " ").title()

        print(f"Processing: {filename}")
        print(f"  Title: {title}")

        try:
            result = await ingestion_pipeline.ingest(
                file_path=file_path,
                title=title,
                author=None,
                tradition=None,
            )
            print(f"  Status: {result['status']}")
            print(f"  Chunks: {result['total_chunks']}")
            print(f"  Techniques: {result['techniques_count']}")
            print(f"  Chunker: {result['chunker_used']}")
            print()
        except Exception as e:
            print(f"  ERROR: {e}")
            print()

    print("Done! Your texts are now indexed and ready for practice generation.")


if __name__ == "__main__":
    asyncio.run(main())
