# services/scorecalc_service.py

async def calculate_score(data: dict) -> dict:
    """
    모든 팀에 대해 norm_sim, MinMax 계산 후
    추천팀 리스트 + 상세근거 포함 state 구조로 반환.
    """

    average_similar_scores_by_team = data["average_similar_scores_by_team"]
    similar_count_by_team = data["similar_count_by_team"]
    load_count_by_team = data["load_count_by_team"]
    max_case_count = data["case_count_max"]
    min_case_count = data["case_count_min"]

    # 파라미터
    a = 0.7
    b = 0.3

    # 팀별 유사도 합계 계산
    similar_sum_by_team = {
        team: avg_sim * similar_count_by_team.get(team, 0)
        for team, avg_sim in average_similar_scores_by_team.items()
    }

    max_sim_sum = max(similar_sum_by_team.values()) if similar_sum_by_team else 1
    max_case = max_case_count
    min_case = min_case_count

    score_by_team = {}
    details = {}

    for team in average_similar_scores_by_team:
        team_sim_sum = similar_sum_by_team.get(team, 0)
        team_sim_count = similar_count_by_team.get(team, 0)

        if team_sim_count > 0:
            norm_sim = team_sim_sum / team_sim_count / max_sim_sum if max_sim_sum else 0
        else:
            norm_sim = 0

        team_case_count = load_count_by_team.get(team, 0)
        denominator = max_case - min_case

        if denominator == 0:
            minmax = 0
        else:
            minmax = (max_case - team_case_count) / denominator

        final_score = round(a * norm_sim + b * minmax, 4)

        score_by_team[team] = final_score
        details[team] = {
            "team_sim_sum": round(team_sim_sum, 4),
            "team_sim_count": team_sim_count,
            "norm_sim": round(norm_sim, 4),
            "MinMax": round(minmax, 4),
            "team_case_count": team_case_count,
            "similar_count": team_sim_count
        }

        print(
            f"[DEBUG] {team} -> sim_sum: {team_sim_sum:.4f}, "
            f"sim_count: {team_sim_count}, norm_sim: {norm_sim:.4f}, "
            f"MinMax: {minmax:.4f}, final_score: {final_score:.4f}"
        )

    max_score = max(score_by_team.values()) if score_by_team else 0

    recommended_teams = [
        team for team, score in score_by_team.items() if score == max_score
    ]

    return {
        "score_by_team": score_by_team,
        "recommended_team": recommended_teams,
        "score": max_score,
        "details": details
    }