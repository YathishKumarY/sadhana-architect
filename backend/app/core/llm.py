from typing import AsyncGenerator

import httpx

from app.config import settings


class OllamaClient:
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.llm_model
        self.temperature = settings.llm_temperature
        self.num_ctx = settings.llm_num_ctx

    async def generate(self, prompt: str, system: str = "") -> str:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": system,
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                        "num_ctx": self.num_ctx,
                    },
                },
            )
            response.raise_for_status()
            return response.json()["response"]

    async def generate_stream(self, prompt: str, system: str = "") -> AsyncGenerator[str, None]:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": system,
                    "stream": True,
                    "options": {
                        "temperature": self.temperature,
                        "num_ctx": self.num_ctx,
                    },
                },
            ) as response:
                response.raise_for_status()
                import json

                async for line in response.aiter_lines():
                    if line.strip():
                        data = json.loads(line)
                        if not data.get("done", False):
                            yield data.get("response", "")

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False


llm_client = OllamaClient()
