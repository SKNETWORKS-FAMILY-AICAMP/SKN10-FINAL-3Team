from sqlalchemy import create_engine
import pandas as pd
from collections import defaultdict
from typing_extensions import TypedDict, Dict, List
from pprint import pprint
import os

# ✅ RDS 연결 엔진 생성
# 예시: mysql+pymysql://username:password@host:port/dbname
DB_URL = os.getenv("DB_URL")  # .env에서 읽기
engine = create_engine(DB_URL)


class State(TypedDict, total=False):
    top_event_ids: List[dict]
    similar_count_by_team: Dict[str, int]
    similar_score_sum_by_team: Dict[str, float]
    average_similar_scores_by_team: Dict[str, float]
    load_count_by_team: Dict[str, int]
    case_count_max: int
    case_count_min: int


def get_code_table() -> pd.DataFrame:
    """
    RDS에서 코드 테이블 조회 → Pandas DataFrame 반환
    """
    sql = "SELECT event_num, org_cd FROM code_table"  # 테이블명에 맞게 수정!
    df = pd.read_sql(sql, engine)
    print("\n✅ [DEBUG] RDS에서 불러온 코드 테이블:")
    pprint(df.head())
    return df


def sqlsearch_node(state: State) -> State:
    """
    vectorsearch 노드의 state (top_event_ids) + RDS 참조
    """
    # ✅ 1) RDS에서 코드 테이블 가져오기
    code_df = get_code_table()

    # ✅ 나머지는 동일
    event_org_map = dict(zip(code_df["event_num"], code_df["org_cd"]))
    print("\n[DEBUG] event_org_map:")
    pprint(event_org_map)

    similar_count_by_team = defaultdict(int)
    similar_score_sum_by_team = defaultdict(float)

    for id_score_dict in state["top_event_ids"]:
        for event_id, score in id_score_dict.items():
            org_cd = event_org_map.get(event_id)
            if org_cd:
                similar_count_by_team[org_cd] += 1
                similar_score_sum_by_team[org_cd] += score

    print("\n[DEBUG] similar_count_by_team:")
    pprint(dict(similar_count_by_team))

    print("\n[DEBUG] similar_score_sum_by_team:")
    pprint(dict(similar_score_sum_by_team))

    average_similar_scores_by_team = {}
    for team in similar_count_by_team:
        cnt = similar_count_by_team[team]
        average = similar_score_sum_by_team[team] / cnt if cnt else 0.0
        average_similar_scores_by_team[team] = round(average, 4)

    print("\n[DEBUG] average_similar_scores_by_team:")
    pprint(average_similar_scores_by_team)

    load_count_by_team = code_df["org_cd"].value_counts().to_dict()
    print("\n[DEBUG] load_count_by_team:")
    pprint(load_count_by_team)

    case_counts = list(load_count_by_team.values())
    case_count_max = max(case_counts) if case_counts else 0
    case_count_min = min(case_counts) if case_counts else 0
    print(f"\n[DEBUG] case_count_max: {case_count_max}, case_count_min: {case_count_min}")

    state.update({
        "similar_count_by_team": dict(similar_count_by_team),
        "similar_score_sum_by_team": dict(similar_score_sum_by_team),
        "average_similar_scores_by_team": average_similar_scores_by_team,
        "load_count_by_team": load_count_by_team,
        "case_count_max": case_count_max,
        "case_count_min": case_count_min
    })

    print("\n✅ [DEBUG] updated state keys:", state.keys())
    return state
