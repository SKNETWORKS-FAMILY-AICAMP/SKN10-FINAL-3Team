from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
from services.ask_llm import generate_markdown_answer, classify_ask_type
import logging
# 로그 설정
logger = logging.getLogger(__name__)

router = APIRouter()

class AskRequest(BaseModel):
    query: str
    case1: Optional[Dict] = None
    case2: Optional[Dict] = None

class AskResponse(BaseModel):
    query_type: str
    answer: str

@router.post("/ask/", response_model=AskResponse)
def handle_query(request: AskRequest):
    """간단한 판례 질문 처리 (복잡한 기능은 /combined 사용)"""
    logger.info(f"AskRequest: {request}")
    query = request.query
    case1 = request.case1
    case2 = request.case2

    query_type = classify_ask_type(query)

    if query_type == "comparison":
        if not (case1 and case2):
            raise HTTPException(status_code=400, detail="판례 비교는 두 판례가 모두 필요합니다.")

        def serialize_case(case: Dict) -> str:
            return "\n\n".join([f"[{k}]\n{v}" for k, v in case.items()])

        case1_info = serialize_case(case1)
        case2_info = serialize_case(case2)

        prompt = f"""
[질문]
{query}

[판례1 정보]
{case1_info}

[판례2 정보]
{case2_info}
"""
        answer = generate_markdown_answer(prompt)
        logger.info(f"Answer: {answer}")
        return AskResponse(query_type="case_comparison", answer=answer)

    elif query_type == "single_case_qa":
        if not case1:
            raise HTTPException(status_code=400, detail="단일 판례 질문은 판례 정보가 필요합니다.")
        
        def serialize_case(case: Dict) -> str:
            return "\n\n".join([f"[{k}]\n{v}" for k, v in case.items()])
        
        case1_info = serialize_case(case1)
        prompt = f"""
[질문]
{query}

[판례 정보]
{case1_info}
"""
        answer = generate_markdown_answer(prompt)
        return AskResponse(query_type="single_case_qa", answer=answer)

    else:  # general
        prompt = f"[질문]\n{query}"
        answer = generate_markdown_answer(prompt)
        return AskResponse(query_type="general", answer=answer)
