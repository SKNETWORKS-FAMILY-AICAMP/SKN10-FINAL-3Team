# models.py
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base
from pydantic import BaseModel
from typing import Optional, Dict, List

# RDB 테이블
## Event 테이블
class Event(Base):
    __tablename__ = 'event'

    event_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    # 사건 기본 정보
    e_description = Column(Text, nullable=False)
    claim_summary = Column(Text, nullable=False)
    client_role = Column(String(10), nullable=False)
    event_file = Column(Text, nullable=True)

    # AI 전략
    ai_strategy = Column(Text, nullable=True, default='미지정')

    # 생성/수정 시간
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    update_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

## Case 테이블
class Case(Base):
    __tablename__ = 'case'

    case_id = Column(Integer, primary_key=True, autoincrement=True, index=True) # 고유ID값
    case_num = Column(Text, nullable=False)                                     # 사건번호
    court_name = Column(Text, nullable=False)                                   # 법원명
    case_at = Column(DateTime(timezone=True), nullable=False)                   # 선고일자
    refer_case = Column(Text, nullable=True)                                    # 참조판례
    refer_statutes = Column(Text, nullable=True)                                # 참조법령
    decision_summary = Column(Text, nullable=True)                              # 판결요지
    case_full = Column(Text, nullable=False)                                    # 판례내용
    decision_issue = Column(Text, nullable=False)                               # 판시사항
    case_result = Column(Text, nullable=False)                                  # 판례결과
    facts_summary = Column(Text, nullable=False)                                # 사실관계 요약
    facts_keywords = Column(Text, nullable=False)                               # 사실관계 키워드
    issue_summary = Column(Text, nullable=False)                                # 쟁점 요약
    issue_keywords = Column(Text, nullable=False)                               # 쟁점 키워드
    keywords = Column(Text, nullable=False)                                     # 키워드

# VectorDB 테이블
# class VectorDB(Base):

# Request / Response 모델
## Event
class EventRequest(BaseModel): 
    event_id: Optional[str] = None
    client_role: str
    e_description: str
    claim_summary: str
    event_file: str

class EventResponse(BaseModel):
    result: str

## Case
class CombinedQueryRequest(BaseModel):
    query: str
    case1: Optional[Dict] = None
    case2: Optional[Dict] = None
    case_ids: Optional[List[int]] = None

class CaseIdQueryRequest(BaseModel):
    query: str
    case_id: int

class CaseIdsQueryRequest(BaseModel):
    query: str
    case_ids: List[int]

# 응답 스키마들
class SimpleResponse(BaseModel):
    answer: str

class DetailedResponse(BaseModel):
    case_ids: List[str]
    answer: str

class CaseResult(BaseModel):
    case_id: str
    title: str
    summary: str
    similarity: float

class CombinedQueryResponse(BaseModel):
    search_type: str  # "조건기반" | "유사도기반" | "일반질문" | "판례비교" | "판례질문"
    case_ids: List[str]
    answer: str
    similar_cases: Optional[List[CaseResult]] = None