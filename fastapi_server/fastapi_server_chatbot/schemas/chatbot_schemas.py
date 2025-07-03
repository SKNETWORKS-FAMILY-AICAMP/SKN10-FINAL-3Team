from pydantic import BaseModel
from typing import List, Union, Optional, Dict

# Request Schemas
class CombinedQueryRequest(BaseModel):
    query: str
    case1: Optional[Dict] = None
    case2: Optional[Dict] = None
    case_ids: Optional[Union[List[int], List[str]]] = None

class CaseIdQueryRequest(BaseModel):
    query: str
    case_id: Optional[int] = None

class CaseIdsQueryRequest(BaseModel):
    query: str
    case_ids: List[int]

# Response Schemas
class SimpleResponse(BaseModel):
    answer: str

class DetailedResponse(BaseModel):
    case_ids: Optional[List[str]] = None
    answer: str

class CaseResult(BaseModel):
    case_id: str
    title: str
    summary: str
    similarity: float

class CombinedQueryResponse(BaseModel):
    search_type: str    # "조건기반" | "유사도기반" | "일반질문" | "판례비교" | "판례질문"
    case_ids: Optional[List[str]] = None
    answer: str
    similar_cases: Optional[List[CaseResult]] = None