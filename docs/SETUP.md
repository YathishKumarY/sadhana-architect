# Setup Guide

Complete step-by-step guide to get Sadhana Architect running on your machine.

## Prerequisites

- macOS or Linux (Windows works with WSL)
- Python 3.11+
- Node.js 18+
- 16GB+ RAM (for running LLM locally)

## Step 1: Install Ollama

Ollama runs LLMs locally on your machine.

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Start Ollama (keep this terminal open):**
```bash
ollama serve
```

**Pull the required models (in a new terminal):**
```bash
# The LLM for generating practices (~4.7GB download)
ollama pull llama3:8b

# The embedding model for text search (~274MB download)
ollama pull nomic-embed-text
```

**Verify:**
```bash
ollama list
# Should show both llama3:8b and nomic-embed-text
```

## Step 2: ChromaDB Setup

ChromaDB is the vector database that stores your text embeddings. It requires NO separate installation or server - it runs embedded inside the Python backend as a library.

When you `pip install -e .` the backend, ChromaDB is installed automatically. It stores data in `backend/data/chroma/` as local files. No database server, no ports, no configuration needed.

That's it. ChromaDB is fully managed by the application code.

## Step 3: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate    # Linux/macOS
# .venv\Scripts\activate     # Windows

# Install all dependencies (includes ChromaDB, FastAPI, etc.)
pip install -e .

# Initialize the SQLite database (creates backend/data/sadhana.db)
python -c "import asyncio; from app.db.session import init_db; asyncio.run(init_db())"

# Verify everything is connected
python ../scripts/verify_ollama.py
```

**Start the backend:**
```bash
uvicorn app.main:app --reload --port 8000
```

Test it: http://localhost:8000/api/v1/health should return:
```json
{"status": "healthy", "ollama": "connected", "llm_model": "llama3:8b", "embedding_model": "nomic-embed-text"}
```

## Step 4: Adding Your Books (PDF/EPUB)

You have two methods:

### Method A: Bulk ingestion via script (recommended for initial setup)

1. Copy all your PDF and EPUB files into `backend/texts/`:
```bash
cp ~/Downloads/yoga-sutras.pdf backend/texts/
cp ~/Downloads/hatha-yoga-pradipika.pdf backend/texts/
cp ~/Downloads/bhagavad-gita.epub backend/texts/
cp ~/Downloads/vijnana-bhairava-tantra.pdf backend/texts/
```

2. Run the seed script:
```bash
cd backend
source .venv/bin/activate
python ../scripts/seed_texts.py
```

This will:
- Parse each file (extract text from PDF/EPUB)
- Auto-detect the text structure (verse, sutra, commentary, prose)
- Chunk intelligently by structure (not arbitrary token windows)
- Generate embeddings via Ollama (nomic-embed-text)
- Store everything in ChromaDB

Output looks like:
```
Found 4 text(s) to ingest:

Processing: yoga-sutras.pdf
  Title: Yoga Sutras
  Status: completed
  Chunks: 196
  Techniques: 47
  Chunker: VerseChunker

Processing: hatha-yoga-pradipika.pdf
  Title: Hatha Yoga Pradipika
  Status: completed
  Chunks: 312
  Techniques: 189
  Chunker: VerseChunker
```

### Method B: Upload via the web UI

1. Start both backend and frontend
2. Go to http://localhost:3000/library
3. Click "Upload Text"
4. Fill in the title, author (optional), tradition (optional)
5. Select your PDF or EPUB file
6. Click "Upload & Process"

The UI shows processing status and chunk count when done.

### Tips for best results

- **File naming**: Name files descriptively (e.g., `hatha-yoga-pradipika-svatmarama.pdf`). The seed script derives the title from the filename.
- **One text per file**: Don't combine multiple books into one PDF.
- **Translations with commentary work best**: Texts that include both the original verse and a translation/commentary produce richer chunks.
- **Tradition tagging**: When uploading via UI, tag the tradition (hatha, raja, tantra, vedanta, bhakti) for better filtered retrieval.

### Recommended starter texts (public domain)

These are freely available online as PDFs:
- Yoga Sutras of Patanjali (any translation with commentary)
- Hatha Yoga Pradipika (Pancham Sinh translation)
- Bhagavad Gita (Swami Sivananda or Eknath Easwaran)
- Vijnana Bhairava Tantra (Lorin Roche or Jaideva Singh)
- Gheranda Samhita
- Shiva Sutras (Jaideva Singh)
- Ashtavakra Gita

## Step 5: Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

## Step 6: First Use

1. Go to http://localhost:3000/settings - create your profile with default preferences
2. Go to http://localhost:3000/library - verify your texts show as "ready"
3. Go to http://localhost:3000/practice - fill in your state and generate!

## Troubleshooting

**"Ollama unreachable" on health check:**
- Make sure `ollama serve` is running in a terminal
- Check if another process is using port 11434: `lsof -i :11434`

**Slow first generation:**
- First request after Ollama starts loads the model into GPU memory (~10-15 seconds)
- Subsequent requests are much faster (5-15 seconds depending on length)

**Empty or poor practice generation:**
- Make sure you've ingested at least 2-3 texts
- Check the library page shows chunks > 0
- Try broader tradition preferences ("Any" instead of specific)

**"No chunks produced" during ingestion:**
- The text might not match any verse/sutra patterns
- Try a different edition of the same text with clearer formatting
- The chapter chunker will be used as fallback for prose texts

**Frontend can't reach backend:**
- Backend must be on port 8000, frontend on port 3000
- The Next.js config proxies /api/* requests to localhost:8000
