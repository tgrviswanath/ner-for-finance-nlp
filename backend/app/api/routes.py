from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.service import extract, extract_batch
import httpx

router = APIRouter(prefix="/api/v1", tags=["ner"])


class TextInput(BaseModel):
    text: str


class BatchInput(BaseModel):
    texts: list[str]


def _handle(e: Exception):
    if isinstance(e, httpx.ConnectError):
        raise HTTPException(status_code=503, detail="NLP service unavailable")
    if isinstance(e, httpx.HTTPStatusError):
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract")
async def extract_endpoint(body: TextInput):
    try:
        return await extract(body.text)
    except Exception as e:
        _handle(e)


@router.post("/extract/batch")
async def extract_batch_endpoint(body: BatchInput):
    try:
        return await extract_batch(body.texts)
    except Exception as e:
        _handle(e)
