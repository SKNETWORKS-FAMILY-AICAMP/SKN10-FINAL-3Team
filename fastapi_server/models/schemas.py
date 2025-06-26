# app/models/schemas.py
from pydantic import BaseModel
from typing import List, Union

# 입력 모델
class SimilarityRequest(BaseModel):
    query: str

# 출력 모델 (각 판례 항목)
class CaseResult(BaseModel):
    case_id: str
    title: str
    summary: str
    similarity: float  # 유사도 점수

# 전체 응답 모델
class SimilarityResponse(BaseModel):
    results: List[CaseResult]

# 분류 요청/응답 모델
class ClassifyRequest(BaseModel):
    query: str

class ClassifyResponse(BaseModel):
    search_type: str  # "조건기반" or "유사도기반"
    filters: dict = {}

# 판례 질문 요청 모델
class AskRequest(BaseModel):
    query: str
    cases: List[dict]  # 판례 1~2개 (meta + contents 포함)
    filters: dict = {}

# 판례 질문 응답 모델
class AskResponse(BaseModel):
    query_type: str  # "case_comparison", "single_case_qa", "similar_case_search"
    answer: str

# 통합 응답 가능 모델
AskOrSimilarityResponse = Union[AskResponse, SimilarityResponse]

# 통합 입력 모델 (/classify → /ask 자동 연결용)
class UnifiedQueryRequest(BaseModel):
    query: str
    cases: List[dict] = []
