import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings


class VectorStore:
    def __init__(self):
        self._client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._chunks_collection = self._client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        self._techniques_collection = self._client.get_or_create_collection(
            name=settings.chroma_techniques_collection,
            metadata={"hnsw:space": "cosine"},
        )

    @property
    def chunks(self):
        return self._chunks_collection

    @property
    def techniques(self):
        return self._techniques_collection

    def add_chunks(self, ids: list[str], documents: list[str], embeddings: list[list[float]], metadatas: list[dict], is_technique: bool = False):
        collection = self._techniques_collection if is_technique else self._chunks_collection
        collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def query(
        self,
        query_embedding: list[float],
        n_results: int = 4,
        where: dict | None = None,
        collection: str = "chunks",
    ) -> dict:
        coll = self._techniques_collection if collection == "techniques" else self._chunks_collection
        kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": n_results,
        }
        if where:
            kwargs["where"] = where
        return coll.query(**kwargs)

    def get_stats(self) -> dict:
        return {
            "chunks_count": self._chunks_collection.count(),
            "techniques_count": self._techniques_collection.count(),
        }


vector_store = VectorStore()
