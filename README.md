# Sadhana Architect

Personalized yoga and spiritual practice generator powered by classical texts and local AI.

## What it does

You describe your current physical, mental, and emotional state. The app retrieves relevant passages from your indexed spiritual texts (Yoga Sutras, Hatha Yoga Pradipika, Bhagavad Gita, etc.) and generates a tailored daily practice with pranayama, asana, and meditation - complete with citations back to source texts.

Everything runs locally. No cloud APIs, no data leaving your machine.

## Stack

- **Backend**: Python FastAPI + SQLAlchemy + ChromaDB
- **Frontend**: Next.js 14 + Tailwind CSS
- **LLM**: Llama 3 8B via Ollama (local)
- **Embeddings**: nomic-embed-text via Ollama
- **Vector DB**: ChromaDB (persistent, local)
- **Database**: SQLite (user profiles, practice history)

## Prerequisites

- Python 3.11+
- Node.js 18+
- [Ollama](https://ollama.com) installed and running

## Setup

### 1. Install Ollama and pull models

```bash
# Install Ollama (macOS)
brew install ollama

# Start Ollama
ollama serve

# Pull required models (in another terminal)
ollama pull llama3:8b
ollama pull nomic-embed-text
```

### 2. Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Initialize database
python -c "import asyncio; from app.db.session import init_db; asyncio.run(init_db())"

# Start the backend
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

### 4. Add your texts

Place your PDF and EPUB spiritual texts in `backend/texts/`, then:

```bash
# Verify Ollama is ready
python scripts/verify_ollama.py

# Ingest all texts
python scripts/seed_texts.py
```

### 5. Use it

Open http://localhost:3000, describe your state, and generate your practice.

## Project Structure

```
backend/
  app/
    api/          - FastAPI route handlers
    core/         - RAG pipeline, LLM client, prompts
    ingestion/    - PDF/EPUB parsers, spiritual text chunkers
    db/           - SQLAlchemy models, ChromaDB wrapper
    schemas/      - Pydantic request/response models
  texts/          - Drop your PDFs/EPUBs here
  data/           - ChromaDB + SQLite storage (auto-created)

frontend/
  src/app/        - Next.js pages (practice, history, library, settings)
  src/components/ - React components
  src/lib/        - API client, TypeScript types
```

## How chunking works

Spiritual texts have precise structure that generic token-window chunking destroys. This app uses four chunking strategies:

- **Verse chunker**: For texts with numbered verses/sutras (Yoga Sutras, Gita, HYP)
- **Commentary chunker**: For texts with sutras + nested commentaries
- **Chapter chunker**: For prose texts with section headings
- **Sliding window**: Fallback for unstructured prose

Each chunk is tagged with `practice_category` (pranayama, asana, meditation, dharana, philosophy) for filtered retrieval.
