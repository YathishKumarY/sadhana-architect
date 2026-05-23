"""Bulk ingest all texts from the backend/texts/ directory.

Tracks which files have already been ingested in a local manifest.
Only new or modified files are processed on subsequent runs.
"""
import asyncio
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.ingestion.pipeline import ingestion_pipeline


TEXTS_DIR = os.path.join(os.path.dirname(__file__), "..", "backend", "texts")
MANIFEST_PATH = os.path.join(os.path.dirname(__file__), "..", "backend", "data", "ingested_manifest.json")


def load_manifest() -> dict:
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH) as f:
            return json.load(f)
    return {}


def save_manifest(manifest: dict):
    os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)


def file_hash(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


async def main():
    files = [
        f for f in os.listdir(TEXTS_DIR)
        if f.endswith((".pdf", ".epub")) and not f.startswith(".")
    ]

    if not files:
        print(f"No PDF or EPUB files found in {TEXTS_DIR}")
        print("Place your spiritual texts there and run this script again.")
        return

    manifest = load_manifest()

    new_files = []
    skipped_files = []

    for filename in sorted(files):
        file_path = os.path.join(TEXTS_DIR, filename)
        current_hash = file_hash(file_path)

        if filename in manifest and manifest[filename]["hash"] == current_hash:
            skipped_files.append(filename)
        else:
            new_files.append(filename)

    print(f"Found {len(files)} text(s) total.")
    if skipped_files:
        print(f"Skipping {len(skipped_files)} already ingested:")
        for f in skipped_files:
            print(f"  [SKIP] {f} ({manifest[f]['chunks']} chunks)")
    print()

    if not new_files:
        print("Nothing new to ingest. All texts are already indexed.")
        return

    print(f"Processing {len(new_files)} new/modified text(s):\n")

    for filename in new_files:
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

            manifest[filename] = {
                "hash": file_hash(file_path),
                "chunks": result["total_chunks"],
                "techniques": result["techniques_count"],
                "chunker": result["chunker_used"],
                "ingested_at": result["ingested_at"],
            }
            save_manifest(manifest)

        except Exception as e:
            print(f"  ERROR: {e}")
            print()

    print("Done! Your texts are now indexed and ready for practice generation.")


if __name__ == "__main__":
    asyncio.run(main())
