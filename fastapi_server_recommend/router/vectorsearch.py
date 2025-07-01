# routers/vectorsearch.py

from fastapi import APIRouter
from services.recommend_team.vectorsearch_service import vector_search

router = APIRouter(prefix="/vectorsearch", tags=["VectorSearch"])

@router.post("/run")
async def run_vectorsearch(data: dict):
    print("[DEBUG] vectorsearch router received data:", data)
    query = data["query"]  # 반드시 dict에서 추출
    result = await vector_search(query)  # str로 전달
    print("[DEBUG] vectorsearch router top_event_ids:", result)

    return {"top_event_ids": result}
