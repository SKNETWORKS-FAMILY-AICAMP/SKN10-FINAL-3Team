from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

def stream_chat_response(case_data_dict: dict, query: str):
    """
    판례 데이터와 사용자 질문을 받아 OpenAI 스트리밍 응답을 생성하는 제너레이터 함수
    """
    # 프롬프트 구성
    prompt = "[사건 정보 요약]\n"
    for key in sorted(case_data_dict.keys()):
        if key.startswith("case"):
            data = case_data_dict[key]
            prompt += f"\n사건번호: {data['case_num']}\n"
            prompt += f"사건명: {data['case_name']}\n"
            prompt += f"판결요지: {data['decision_summary'][:300]}...\n"

    prompt += f"\n\n[사용자 질문]\n{query}"

    # Chat Completions (Streaming)
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            # model="khs2617/gemma-3-1b-it-merged_model_strategy",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 민사 소송 전문가입니다. 판례를 바탕으로 전략적 분석을 제공합니다."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            stream=True,
            temperature=0.7,
        )

        for chunk in response:
            content = chunk.choices[0].delta.content
            if isinstance(content, str):
                yield content

    except Exception as e:
        print("❌ OpenAI 호출 오류:", e)
        yield "⚠️ 답변을 생성하는 중 오류가 발생했습니다."

def get_chat_response(case_data_dict: dict, query: str) -> str:
    """
    판례 데이터와 사용자 질문을 받아 OpenAI 응답을 생성하는 비스트리밍 함수
    """
    prompt = "[사건 정보 요약]\n"
    for key in sorted(case_data_dict.keys()):
        if key.startswith("case"):
            data = case_data_dict[key]
            prompt += f"\n사건번호: {data['case_num']}\n"
            prompt += f"사건명: {data['case_name']}\n"
            prompt += f"판결요지: {data['decision_summary'][:300]}...\n"

    prompt += f"\n\n[사용자 질문]\n{query}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 민사 소송 전문가입니다. 판례를 바탕으로 전략적 분석을 제공합니다."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            stream=False,
            temperature=0.7,
            max_tokens=1024,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("❌ OpenAI 호출 오류:", e)
        return "⚠️ 답변을 생성하는 중 오류가 발생했습니다."
