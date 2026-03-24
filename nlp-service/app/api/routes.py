from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.service import extract_entities

router = APIRouter(prefix="/api/v1/nlp", tags=["finance-ner"])


class TextInput(BaseModel):
    text: str


class BatchInput(BaseModel):
    texts: list[str]


@router.post("/extract")
def extract(body: TextInput):
    if not body.text.strip():
        raise HTTPException(status_code=400, detail="text cannot be empty")
    try:
        return extract_entities(body.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract/batch")
def extract_batch(body: BatchInput):
    if not body.texts:
        raise HTTPException(status_code=400, detail="texts list cannot be empty")
    try:
        return [extract_entities(t) for t in body.texts]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
