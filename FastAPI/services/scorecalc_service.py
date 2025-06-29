# services/scorecalc_service.py

async def calculate_score(data: dict) -> dict:
    """
    모든 팀에 대해 norm_sim, MinMax 계산 후
    추천팀 + 상세근거 포함 state 구조로 반환.
    """

    average_similar_scores_by_team = data["average_similar_scores_by_team"]
    similar_count_by_team = data["similar_count_by_team"]
    load_count_by_team = data["load_count_by_team"]
    max_case_count = data["case_count_max"]
    min_case_count = data["case_count_min"]

    # 파라미터
    a = 0.7
    b = 0.3

    max_sim = max(average_similar_scores_by_team.values()) if average_similar_scores_by_team else 1
    max_case = max(load_count_by_team.values()) if load_count_by_team else 1
    min_case = min(load_count_by_team.values()) if load_count_by_team else 0

    score_by_team = {}
    details = {}

    for team, avg_sim in average_similar_scores_by_team.items():
        # team_sim은 평균 유사도 값 사용
        team_sim = avg_sim
        norm_sim = team_sim / max_sim if max_sim else 0

        team_case_count = load_count_by_team.get(team, 0)
        denominator = max_case - min_case

        if denominator == 0:
            minmax = 0
        else:
            minmax = (max_case - team_case_count) / denominator

        final_score = round(a * norm_sim + b * minmax, 4)

        score_by_team[team] = final_score
        details[team] = {
            "team_sim": round(team_sim, 4),
            "norm_sim": round(norm_sim, 4),
            "MinMax": round(minmax, 4),
            "team_case_count": team_case_count,
            "similar_count": similar_count_by_team.get(team, 0)  # 참고로 추가
        }

        print(
            f"[DEBUG] {team} -> team_sim: {team_sim:.4f}, "
            f"norm_sim: {norm_sim:.4f}, MinMax: {minmax:.4f}, "
            f"final_score: {final_score:.4f}"
        )

    recommended_team = max(score_by_team, key=score_by_team.get)
    recommended_score = score_by_team[recommended_team]

    return {
        "score_by_team": score_by_team,
        "recommended_team": recommended_team,
        "score": recommended_score,
        "details": details
    }
