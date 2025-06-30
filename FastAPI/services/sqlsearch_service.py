from sqlalchemy import create_engine, text
import pandas as pd
from collections import defaultdict
from typing_extensions import TypedDict, Dict, List
from pprint import pprint
import os, re

# RDS 연결 엔진
DB_URL = os.getenv("DB_URL")
engine = create_engine(DB_URL)


class State(TypedDict, total=False):
    top_event_ids: List[dict]
    similar_count_by_team: Dict[str, int]
    average_similar_scores_by_team: Dict[str, float]
    load_count_by_team: Dict[str, int]
    case_count_max: int
    case_count_min: int


def get_code_table() -> pd.DataFrame:
    """
    사건(Event) + 코드(Code_T) 조인 → 사건별 조직코드, 팀 라벨 매핑
    """
    sql = """
    SELECT e.event_num, e.org_cd, c.code_label
    FROM event AS e
    JOIN code_t AS c ON e.org_cd = c.code
    """
    df = pd.read_sql(sql, engine)
    print("\n[DEBUG] 조인 쿼리 결과:")
    pprint(df.head())
    return df


def get_load_count_by_team() -> Dict[str, int]:
    """
    현재 진행중인 사건만 팀별로 카운트
    estat_cd != 'ESTAT_01_12' 조건 적용
    """
    sql = """
    SELECT org_cd, COUNT(*) AS count
    FROM event
    WHERE estat_cd != 'ESTAT_01_12'
    GROUP BY org_cd
    """
    df = pd.read_sql(sql, engine)
    load_count = dict(zip(df["org_cd"], df["count"]))
    print("\n[DEBUG] 진행중 사건 load_count_by_team:")
    pprint(load_count)
    return load_count


def map_team_code_to_label(source: Dict[str, any], mapper: Dict[str, str]) -> Dict[str, any]:
    """
    출력 시 팀 코드 → 라벨로 변환.
    mapper 기준으로 모든 팀 포함, source에 없으면 0
    """
    result = {}
    for code, label in mapper.items():
        result[label] = source.get(code, 0)
    return result


def get_available_teams_for_cat_cd(cat_cd: str) -> Dict[str, str]:
    """
    custom_user + code_t 조인
    CAT_01 → ORG_01_% 형태로 패턴 만들어서 org_cd → label 맵 가져오기
    """
    match = re.search(r'CAT_(\d+)', cat_cd)
    if not match:
        print(f"[WARN] cat_cd 패턴이 이상함: {cat_cd}")
        return {}

    org_num = match.group(1)
    pattern = f"ORG_{org_num}_%"

    sql = text("""
        SELECT DISTINCT u.org_cd, c.code_label 
        FROM custom_user AS u
        JOIN code_t AS c ON u.org_cd = c.code
        WHERE u.org_cd LIKE :pattern
    """)
    df = pd.read_sql(sql, engine, params={"pattern": pattern})
    result = dict(zip(df["org_cd"], df["code_label"]))
    print("\n[DEBUG] get_available_teams_for_cat_cd:", result)
    return result


def sqlsearch_node(state: State) -> State:
    print("\n[DEBUG] sqlsearch_node() called with state:")
    pprint(state)

    code_df = get_code_table()
    event_org_map = dict(zip(code_df["event_num"], code_df["org_cd"]))

    cat_cd = state["cat_cd"]
    print(f"\n[DEBUG] cat_cd in sqlsearch_node: {cat_cd}")
    all_team_map = get_available_teams_for_cat_cd(cat_cd)
    all_team_codes = set(all_team_map.keys())

    similar_count_by_team = defaultdict(int)
    similar_score_sum_by_team = defaultdict(float)

    for id_score_dict in state["top_event_ids"]:
        for event_id, score in id_score_dict.items():
            org_cd = event_org_map.get(str(event_id).strip())
            if org_cd:
                similar_count_by_team[org_cd] += 1
                similar_score_sum_by_team[org_cd] += score
            else:
                print(f"[WARN] 매칭 실패: {event_id}")

    for code in all_team_codes:
        similar_count_by_team.setdefault(code, 0)
        similar_score_sum_by_team.setdefault(code, 0.0)

    average_similar_scores_by_team = {}
    for code in all_team_codes:
        cnt = similar_count_by_team[code]
        avg = similar_score_sum_by_team[code] / cnt if cnt else 0.0
        average_similar_scores_by_team[code] = round(avg, 4)

    load_count_by_team = get_load_count_by_team()
    for code in all_team_codes:
        load_count_by_team.setdefault(code, 0)

    state.update({
        "similar_count_by_team": map_team_code_to_label(dict(similar_count_by_team), all_team_map),
        "average_similar_scores_by_team": map_team_code_to_label(average_similar_scores_by_team, all_team_map),
        "load_count_by_team": map_team_code_to_label(load_count_by_team, all_team_map),
        "case_count_max": max(load_count_by_team.values()),
        "case_count_min": min(load_count_by_team.values())
    })

    return state
