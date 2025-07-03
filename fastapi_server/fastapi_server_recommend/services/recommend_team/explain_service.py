from models.gpt import ask_gpt
import json
from sqlalchemy import create_engine, text

async def generate_explanation(data: dict) -> str:
    """
    여러 팀을 한 줄 요약으로 설명한다.
    """
    recommended_teams = data["recommended_team"]
    details = data["details"]
    score_by_team = data.get("score_by_team")

    team_list_str = ", ".join(recommended_teams)
    details_json = json.dumps(details, ensure_ascii=False, indent=2)
    score_json = json.dumps(score_by_team, ensure_ascii=False, indent=2) if score_by_team else "없음"

    messages = [
        {
            "role": "system",
            "content": (
                "너는 법무법인 사건 배정 추천 시스템의 AI 설명 노드입니다.\n"
                "추천 사유는 팀명을 언급하지 않고 추천된 팀과 추천되지 않은 팀을 비교하여 한 문장으로 간결하고 자연스럽게 요약해주세요.\n"
                "추천 점수는 전문성(norm_sim)과 업무량(MinMax)의 가중합으로 계산됩니다.\n"
                "전문성이 낮아도 현재 업무량이 적으면 점수가 높아져 추천될 수 있음을 반드시 반영해주세요.\n"
                "추천되지 않은 팀이 있다면 왜 제외되었는지도 짧게 포함해주시면 좋겠습니다.\n"
                "부디 계산 과정은 언급하지 말고, 120자 이내로 부탁드립니다. 감사합니다."
            )
        },
        {
            "role": "user",
            "content": (
                f"추천팀: [{team_list_str}]\n"
                f"팀별 최종 점수: {score_json}\n"
                f"팀별 세부 지표: {details_json}\n"
                "추천된 팀이 왜 선택되었고 다른 팀은 왜 제외되었는지를 팀명을 사용하지 않고 "
                "자연스럽고 간결하게 한 문장으로 설명해주세요. 감사합니다."
            )
        }
    ]

    explanation = ask_gpt(
        system_prompt=messages[0]["content"],
        user_prompt=messages[1]["content"],
        model="gpt-4o-mini",
        temperature=0.2,
    )
    print("[DEBUG] explain_service explanation:", explanation)
    return explanation