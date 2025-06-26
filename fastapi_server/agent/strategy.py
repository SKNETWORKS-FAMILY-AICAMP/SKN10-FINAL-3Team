import os
from openai import OpenAI

RUNPOD_API_URL = os.getenv("RUNPOD_API_URL")
RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")

client = OpenAI(
        base_url=RUNPOD_API_URL,
        api_key=RUNPOD_API_KEY
    )

# 요청 프롬프트 생성 함수
def __get_request_prompt(request):
    if request.client_role == "피고":
        system_prompt = f"""다음 사건에 대한 {request.client_role} 전략을 제시해주세요.
출력 양식:
### 전략 방향성:
- ...
### 방어 논리:
- ...
### 참고 사항:
- ...
"""
    elif request.client_role == "원고":
        system_prompt = f"""다음 사건에 대한 {request.client_role} 전략을 제시해주세요.
출력 양식:
### 전략 방향성:
- ...
### 방어 논리:
- ...
### 참고 사항:
- ...
"""
    user_prompt = f"""
사건 내용: {request.e_description}
주장 요약: {request.claim_summary}
증거자료: {request.event_file}
"""
    return system_prompt, user_prompt

# 전략 생성 함수
def generate_strategy(request):
    system_prompt, user_prompt = __get_request_prompt(request)
    response = client.chat.completions.create(
        model="khs2617/gemma-3-1b-it-merged_model_strategy",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}],
        max_tokens=1000,
        temperature=0.1
    )
    strategy = response.choices[0].message.content
    return strategy