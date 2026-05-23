from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    app_name: str = "Sadhana Architect"
    debug: bool = False

    ollama_base_url: str = "http://localhost:11434"
    llm_model: str = "llama3:8b"
    embedding_model: str = "nomic-embed-text"

    chroma_persist_dir: str = str(Path(__file__).parent.parent / "data" / "chroma")
    chroma_collection_name: str = "text_chunks"
    chroma_techniques_collection: str = "practice_techniques"

    sqlite_url: str = f"sqlite+aiosqlite:///{Path(__file__).parent.parent / 'data' / 'sadhana.db'}"

    texts_dir: str = str(Path(__file__).parent.parent / "texts")

    llm_temperature: float = 0.7
    llm_num_ctx: int = 8192
    retrieval_top_k: int = 4

    class Config:
        env_prefix = "SADHANA_"
        env_file = ".env"


settings = Settings()
