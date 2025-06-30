# routers/explain.py

from fastapi import APIRouter
from services.explain_service import generate_explanation

router = APIRouter(prefix="/explain", tags=["Explain"])

@router.post("/run")
async def run_explain(data: dict):
    explanation = await generate_explanation(data)
    return {"explanation": explanation}
