# Deployment Guide

Options for making Sadhana Architect accessible beyond your local machine.

## Option 1: Local Network (share with household)

The simplest "deployment" - run on one machine, access from other devices on your WiFi.

```bash
# Backend - bind to all interfaces
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend - bind to all interfaces
cd frontend
npm run dev -- --hostname 0.0.0.0
```

Find your local IP:
```bash
# macOS
ipconfig getifaddr en0

# Linux
hostname -I | awk '{print $1}'
```

Access from any device on your network: `http://192.168.x.x:3000`

## Option 2: Docker Compose (portable local setup)

Package everything into containers for easy setup on any machine.

**docker-compose.yml:**
```yaml
services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]  # Remove if no GPU

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - SADHANA_OLLAMA_BASE_URL=http://ollama:11434
    volumes:
      - ./backend/texts:/app/texts
      - backend_data:/app/data
    depends_on:
      - ollama

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  ollama_data:
  backend_data:
```

**backend/Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml .
RUN pip install -e .

COPY app/ app/
COPY texts/ texts/
RUN mkdir -p data

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**frontend/Dockerfile:**
```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

**Run:**
```bash
docker compose up -d

# Pull models inside the Ollama container (first time only)
docker compose exec ollama ollama pull llama3:8b
docker compose exec ollama ollama pull nomic-embed-text

# Ingest texts
docker compose exec backend python /app/../scripts/seed_texts.py
```

## Option 3: Cloud VM with GPU (accessible anywhere)

For running the full app with local LLM on a cloud server.

### Recommended providers:
- **RunPod** - GPU instances from $0.20/hr (best for Ollama)
- **Vast.ai** - Cheap GPU rentals
- **Lambda Labs** - A10G instances
- **Hetzner** - Budget VPS (CPU-only, slower but cheapest)

### Setup on a GPU cloud VM:

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
ollama pull llama3:8b
ollama pull nomic-embed-text

# Clone and setup
git clone https://github.com/YathishKumarY/sadhana-architect.git
cd sadhana-architect

# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e .
python -c "import asyncio; from app.db.session import init_db; asyncio.run(init_db())"

# Upload your texts via scp
# scp ~/texts/*.pdf user@server:/path/to/sadhana-architect/backend/texts/
python ../scripts/seed_texts.py

# Start backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Frontend
cd ../frontend
npm install
npm run build
npm start -- --hostname 0.0.0.0 &
```

**Add HTTPS with Caddy (recommended for public access):**
```bash
# Install Caddy
sudo apt install caddy

# /etc/caddy/Caddyfile
yourdomain.com {
    reverse_proxy localhost:3000
}

sudo systemctl restart caddy
```

## Option 4: Split Architecture (API-based LLM)

If you want to deploy the web app cheaply but don't want to run a GPU server, you can swap the local Ollama backend for a cloud LLM API.

**Modify `backend/app/core/llm.py` to use an API:**

Replace Ollama calls with:
- **Groq** (free tier, runs Llama 3 on their hardware) - fastest
- **Together.ai** (cheap, many open models)
- **OpenRouter** (routes to cheapest available provider)

This lets you deploy the backend on a $5/month VPS (no GPU needed) and only pay per-request for LLM inference.

Example change for Groq:
```python
# In backend/app/config.py, add:
groq_api_key: str = ""
llm_provider: str = "ollama"  # or "groq"

# In backend/app/core/llm.py, add a GroqClient alternative
```

The embeddings can also use a free hosted model (Hugging Face Inference API) instead of local nomic-embed-text.

## Option 5: Vercel + Railway (fully managed)

**Frontend on Vercel (free):**
```bash
cd frontend
npx vercel
```

Update `next.config.js` to point to your backend URL instead of localhost.

**Backend on Railway ($5/month):**
```bash
# Railway auto-detects Python projects
# Set environment variables in Railway dashboard:
SADHANA_OLLAMA_BASE_URL=http://your-ollama-server:11434
```

You'll still need Ollama running somewhere (a GPU VM or use the API swap from Option 4).

## Recommended Path

1. **Start local** - develop and test on your laptop
2. **Docker Compose** - package it up, share with friends
3. **Groq swap + cheap VPS** - if you want it accessible from your phone anywhere
4. **GPU cloud** - if you want full local-LLM privacy without carrying your laptop

## Environment Variables for Deployment

```bash
# Required
SADHANA_OLLAMA_BASE_URL=http://localhost:11434  # or remote Ollama URL
SADHANA_LLM_MODEL=llama3:8b
SADHANA_EMBEDDING_MODEL=nomic-embed-text

# Optional
SADHANA_DEBUG=false
SADHANA_LLM_TEMPERATURE=0.7
SADHANA_LLM_NUM_CTX=8192
SADHANA_RETRIEVAL_TOP_K=4
```

## Security Notes

- This app has NO authentication by default (single-user local app)
- If deploying publicly, add auth (e.g., HTTP Basic Auth via Caddy, or add FastAPI auth middleware)
- Never expose the Ollama port (11434) to the internet without auth
- The SQLite database and ChromaDB store your practice history locally - back them up from `backend/data/`
