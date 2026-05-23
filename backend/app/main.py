from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import practice, ingest, users, history

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(practice.router, prefix="/api/v1/practice", tags=["practice"])
app.include_router(ingest.router, prefix="/api/v1/ingest", tags=["ingest"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(history.router, prefix="/api/v1/history", tags=["history"])


@app.get("/api/v1/health")
async def health_check():
    import httpx

    ollama_ok = False
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{settings.ollama_base_url}/api/tags")
            ollama_ok = resp.status_code == 200
    except Exception:
        pass

    return {
        "status": "healthy" if ollama_ok else "degraded",
        "ollama": "connected" if ollama_ok else "unreachable",
        "llm_model": settings.llm_model,
        "embedding_model": settings.embedding_model,
    }
