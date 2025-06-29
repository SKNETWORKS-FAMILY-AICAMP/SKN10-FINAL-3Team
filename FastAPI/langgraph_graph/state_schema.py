from typing import TypedDict, Dict

# 1) 상태 스키마 정의 (TypedDict 버전)
# LangGraph가 상태로 관리할 모든 Key를 정의하는 구조
class GraphState(TypedDict, total=False):
    cat_cd: str
    e_description: str
    score_by_team: Dict[str, float]
    recommended_team: str
    score: float
    details: Dict[str, dict]
    explanation: str