from models.vllm import generate_strategy
from services.strategy import get_request_prompt
from fastapi import APIRouter, HTTPException, Depends
from schemas import EventRequest, EventResponse
from sqlalchemy.orm import Session
from database import get_db
from db.event_db import Event
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/add-strategy/", response_model=EventResponse)
async def analyze_case(event: EventRequest):
    """
    사건 등록 시 sLLM 모델을 통해 전략 생성
    Args:
        event: 사건 정보
            - client_role: 원고/피고
            - e_description: 사건 내용
            - claim_summary: 청구 내용용
            - event_file: 증거자료
    Returns:
        EventResponse: 전략 생성 결과
            - result: 전략 생성 결과
    """
    try:
        logger.info(f"분석 요청 받음: {event}")
        # 시스템 프롬프트와 유저 프롬프트 생성
        system_prompt, user_prompt = get_request_prompt(event)
        # LLM 모델을 통해 전략 생성
        strategy = generate_strategy(system_prompt, user_prompt)
        logger.info(f"전략 생성 결과: {strategy}")
        return EventResponse(result=strategy)
    except Exception as e:
        logger.error(f"분석 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"분석 중 오류가 발생했습니다: {str(e)}")

@router.post("/update-strategy/", response_model=EventResponse)
async def update_ai_strategy(event: EventRequest, db: Session = Depends(get_db)):
    """
    사건 수정 시 전략 생성
    Args:
        event: 사건 정보
            - client_role: 원고/피고
            - e_description: 사건 내용
            - claim_summary: 청구 내용
            - event_file: 증거자료
    Returns:
        EventResponse: 전략 생성 결과
            - result: 전략 생성 결과
    """
    try:
        logger.info(f"분석 요청 받음: {event.client_role}")
        # 시스템 프롬프트와 유저 프롬프트 생성
        system_prompt, user_prompt = get_request_prompt(event)
        # LLM 모델을 통해 전략 생성
        strategy = generate_strategy(system_prompt, user_prompt)
        print(f"DEBUG: 전략 생성 결과: {strategy}")
        # 후처리
        strategy = strategy.replace("\n ", "\n")
        # 사건 정보 업데이트
        event = db.query(Event).filter(Event.event_id == event.event_id).first()
        event.ai_strategy = strategy
        db.commit()
        logger.info(f"전략 생성 결과: {strategy}")
        return EventResponse(result=strategy)

    except Exception as e:
        logger.error(f"분석 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"분석 중 오류가 발생했습니다: {str(e)}")
