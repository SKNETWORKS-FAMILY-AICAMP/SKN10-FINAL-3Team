from openai import OpenAI
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

client = OpenAI()

async def generate_explanation(data: dict) -> str:
    """
    모든 팀의 details를 LLM에 넘겨 상대 비교 기반 추천 사유 작성.
    """
    recommended_team = data["recommended_team"]
    score = data["score"]
    details = data["details"]

    print("[DEBUG] recommended_team:", recommended_team)
    print("[DEBUG] generate_explanation details:", details)
    print("[DEBUG] recommended_team details:", details.get(recommended_team))

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
                    "추천된 팀이 다른 팀보다 어떤 점에서 상대적으로 적합한지 "
                    "비교하여 한 문장으로 50자 이내로 작성해라."
                )
            },
            {
                "role": "user",
                "content": (
                    f"추천팀: '{recommended_team}', 점수: {score:.2f}\n"
                    f"모든 팀 세부 점수: {details}\n"
                    "이 정보를 바탕으로 추천 사유를 작성해줘."
                )
            }
        ]
    )

    explanation = response.choices[0].message.content.strip()
    return explanation
