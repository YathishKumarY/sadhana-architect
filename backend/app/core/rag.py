import json
from typing import AsyncGenerator

from app.core.llm import llm_client
from app.core.embeddings import embedding_service
from app.core.prompts import PRACTICE_GENERATION_SYSTEM_PROMPT, build_practice_prompt
from app.db.vector_store import vector_store
from app.schemas.practice import PracticeRequest, GeneratedPractice


class RAGPipeline:
    async def _build_retrieval_queries(self, request: PracticeRequest) -> list[dict]:
        """Build multiple semantic queries for diverse retrieval."""
        queries = []

        if "pranayama" in request.focus_areas or "asana" in request.focus_areas:
            queries.append({
                "text": f"yoga practice technique for {request.physical_state} "
                        f"suitable for {request.experience_level} practitioner",
                "collection": "techniques",
                "where": self._build_technique_filter(request),
            })

        queries.append({
            "text": f"teachings about {request.mental_state} {request.emotional_state} "
                    f"spiritual guidance for inner state",
            "collection": "chunks",
            "where": self._build_tradition_filter(request),
        })

        if "meditation" in request.focus_areas:
            queries.append({
                "text": f"meditation dharana technique for {request.emotional_state} "
                        f"{request.time_available_minutes} minutes practice",
                "collection": "techniques",
                "where": {"practice_category": {"$in": ["meditation", "dharana"]}},
            })

        return queries

    def _build_technique_filter(self, request: PracticeRequest) -> dict | None:
        filters = []
        if request.tradition_preference:
            filters.append({"tradition": request.tradition_preference})

        categories = [a for a in request.focus_areas if a in ["pranayama", "asana", "meditation", "dharana", "mantra"]]
        if categories:
            filters.append({"practice_category": {"$in": categories}})

        if len(filters) == 0:
            return None
        if len(filters) == 1:
            return filters[0]
        return {"$and": filters}

    def _build_tradition_filter(self, request: PracticeRequest) -> dict | None:
        if request.tradition_preference:
            return {"tradition": request.tradition_preference}
        return None

    async def retrieve(self, request: PracticeRequest) -> list[dict]:
        """Retrieve relevant chunks from vector store."""
        queries = await self._build_retrieval_queries(request)
        all_chunks = []
        seen_ids = set()

        for query_spec in queries:
            query_embedding = await embedding_service.embed(query_spec["text"])
            results = vector_store.query(
                query_embedding=query_embedding,
                n_results=4,
                where=query_spec.get("where"),
                collection=query_spec["collection"],
            )

            if results and results.get("documents"):
                for i, doc in enumerate(results["documents"][0]):
                    chunk_id = results["ids"][0][i] if results.get("ids") else f"chunk_{i}"
                    if chunk_id not in seen_ids:
                        seen_ids.add(chunk_id)
                        metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
                        all_chunks.append({
                            "id": chunk_id,
                            "text": doc,
                            "metadata": metadata,
                        })

        return all_chunks

    async def generate(self, request: PracticeRequest) -> GeneratedPractice:
        """Full RAG pipeline: retrieve then generate."""
        chunks = await self.retrieve(request)

        prompt = build_practice_prompt(
            physical_state=request.physical_state,
            mental_state=request.mental_state,
            emotional_state=request.emotional_state,
            time_minutes=request.time_available_minutes,
            experience_level=request.experience_level,
            tradition=request.tradition_preference,
            focus_areas=request.focus_areas,
            exclude=request.exclude,
            retrieved_chunks=chunks,
        )

        response_text = await llm_client.generate(
            prompt=prompt,
            system=PRACTICE_GENERATION_SYSTEM_PROMPT,
        )

        practice_data = self._parse_response(response_text)
        return GeneratedPractice(**practice_data)

    async def generate_stream(self, request: PracticeRequest) -> AsyncGenerator[str, None]:
        """Streaming version - yields chunks of text as LLM generates."""
        chunks = await self.retrieve(request)

        prompt = build_practice_prompt(
            physical_state=request.physical_state,
            mental_state=request.mental_state,
            emotional_state=request.emotional_state,
            time_minutes=request.time_available_minutes,
            experience_level=request.experience_level,
            tradition=request.tradition_preference,
            focus_areas=request.focus_areas,
            exclude=request.exclude,
            retrieved_chunks=chunks,
        )

        full_response = ""
        async for token in llm_client.generate_stream(
            prompt=prompt,
            system=PRACTICE_GENERATION_SYSTEM_PROMPT,
        ):
            full_response += token
            yield token

        yield "\n[DONE]"

    def _parse_response(self, text: str) -> dict:
        """Parse LLM JSON response, handling common formatting issues."""
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            start = cleaned.find("{")
            end = cleaned.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(cleaned[start:end])
            raise ValueError(f"Could not parse LLM response as JSON: {text[:200]}")


rag_pipeline = RAGPipeline()
