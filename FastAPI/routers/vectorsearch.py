# routers/vectorsearch.py

from fastapi import APIRouter
from services.vectorsearch_service import vector_search

router = APIRouter(prefix="/vectorsearch", tags=["VectorSearch"])

@router.post("/run")
async def run_vectorsearch(data: dict):
    result = await vector_search(data)
    print("[DEBUG] vectorsearch router top_event_ids:", result)
    return {"top_event_ids": result}
