import httpx
from app.core.config import settings

NLP_URL = settings.NLP_SERVICE_URL


async def extract(text: str) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{NLP_URL}/api/v1/nlp/extract",
            json={"text": text},
            timeout=30.0,
        )
        r.raise_for_status()
        return r.json()


async def extract_batch(texts: list[str]) -> list:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{NLP_URL}/api/v1/nlp/extract/batch",
            json={"texts": texts},
            timeout=60.0,
        )
        r.raise_for_status()
        return r.json()
