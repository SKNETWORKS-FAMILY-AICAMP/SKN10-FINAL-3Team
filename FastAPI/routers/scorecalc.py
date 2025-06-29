# routers/scorecalc.py

from fastapi import APIRouter
from services.scorecalc_service import calculate_score

router = APIRouter(prefix="/scorecalc", tags=["ScoreCalc"])

@router.post("/run")
async def run_scorecalc(data: dict):
    # 실제 서비스 함수 호출
    result = await calculate_score(data)
    print("[DEBUG] scorecalc router result:", result)
    return result
