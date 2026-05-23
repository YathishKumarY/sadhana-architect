"""Verify Ollama is running and required models are available."""
import asyncio
import httpx
import sys


REQUIRED_MODELS = ["llama3:8b", "nomic-embed-text"]
OLLAMA_URL = "http://localhost:11434"


async def main():
    print("Checking Ollama connection...")

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{OLLAMA_URL}/api/tags")
            resp.raise_for_status()
    except Exception as e:
        print(f"ERROR: Cannot connect to Ollama at {OLLAMA_URL}")
        print(f"  {e}")
        print("\nMake sure Ollama is running:")
        print("  ollama serve")
        sys.exit(1)

    print("  Connected to Ollama")

    models = resp.json().get("models", [])
    model_names = [m["name"] for m in models]

    all_found = True
    for required in REQUIRED_MODELS:
        found = any(required in name for name in model_names)
        status = "OK" if found else "MISSING"
        print(f"  [{status}] {required}")
        if not found:
            all_found = False

    if not all_found:
        print("\nPull missing models:")
        for required in REQUIRED_MODELS:
            if not any(required in name for name in model_names):
                print(f"  ollama pull {required}")
        sys.exit(1)

    print("\nAll models available. Ready to go!")


if __name__ == "__main__":
    asyncio.run(main())
