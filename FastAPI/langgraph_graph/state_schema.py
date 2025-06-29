from typing import TypedDict, Dict, List

# 1) 상태 스키마 정의 (TypedDict 버전)
# LangGraph가 상태로 관리할 모든 Key를 정의하는 구조
class GraphState(TypedDict, total=False):
    cat_cd: str
    e_description: str
    top_event_ids: List[Dict[str, float]] 
    similar_count_by_team: Dict[str, int]
    average_similar_scores_by_team: Dict[str, float]
    load_count_by_team: Dict[str, int]
    case_count_max: int
    case_count_min: int
    score_by_team: Dict[str, float]
    recommended_team: str
    score: float
    details: Dict[str, dict]
    explanation: str