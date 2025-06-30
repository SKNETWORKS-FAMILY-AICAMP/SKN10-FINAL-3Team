from openai import OpenAI
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import os

# .env 파일에서 환경 변수 로드
load_dotenv()

client = OpenAI()

async def generate_explanation(data: dict) -> str:
    """
    동점 팀이 여러 개일 경우도 LLM에 넘겨 상대 비교 기반 추천 사유 작성.
    """
    recommended_teams = data["recommended_team"]
    score = data["score"]
    details = data["details"]

    print("[DEBUG] recommended_team:", recommended_teams)
    print("[DEBUG] generate_explanation details:", details)

    # 동점 팀별 상세 디버깅
    for team in recommended_teams:
        print(f"[DEBUG] details for {team}:", details.get(team))

    # 여러 팀일 경우를 위해 문자열로 포맷
    team_list_str = ", ".join(recommended_teams)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.3,
        messages=[
            {
                "role": "system",
                "content": (
                    "너는 법무법인 사건 배정 추천 시스템의 AI 설명 노드야. "
                    "아래 details는 모든 팀의 점수와 부하 정보야.\n"
                    "- norm_sim는 전문성을 나타냄 (높을수록 좋음)\n"
                    "- MinMax는 업무량을 나타냄 (높을수록 적은 업무)\n"
                    "추천된 팀들이 다른 팀보다 어떤 점에서 상대적으로 적합한지 "
                    "간략히 비교해서 50자 이내로 설명해라."
                )
            },
            {
                "role": "user",
                "content": (
                    f"추천팀들: [{team_list_str}], 점수: {score:.2f}\n"
                    f"모든 팀 세부 점수: {details}\n"
                    f"이 정보를 바탕으로 추천 사유를 작성해줘.\n"
                    f"각 팀의 norm_sim과 MinMax를 고려하여, 왜 이 팀들이 추천되었는지 자세하게 설명하되,\n"
                    "50자 이내로 요약해줘.\n"
                )
            }
        ]
    )

    explanation = response.choices[0].message.content.strip()
    return explanation
