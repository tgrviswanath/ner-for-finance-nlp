import asyncio
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.service import extract_entities

router = APIRouter(prefix="/api/v1/nlp", tags=["finance-ner"])


class TextInput(BaseModel):
    text: str


class BatchInput(BaseModel):
    texts: list[str]


@router.post("/extract")
async def extract(body: TextInput):
    if not body.text.strip():
        raise HTTPException(status_code=400, detail="text cannot be empty")
    try:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, extract_entities, body.text)
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract/batch")
async def extract_batch(body: BatchInput):
    if not body.texts:
        raise HTTPException(status_code=400, detail="texts list cannot be empty")
    try:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: [extract_entities(t) for t in body.texts])
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
