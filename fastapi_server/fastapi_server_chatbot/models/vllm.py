import os
from openai import OpenAI

# vllm 클라이언트 호출 함수
RUNPOD_API_URL = os.getenv("RUNPOD_API_URL")
RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
model_name = "khs2617/gemma-3-1b-it-fft"

def get_vllm() -> OpenAI:
  """
  Runpod API를 통해 vllm 클라이언트 호출 함수
  Args:
    None
  Returns:
    OpenAI: vllm 클라이언트
  """
  client = OpenAI(
    base_url=RUNPOD_API_URL,
    api_key=RUNPOD_API_KEY
  )
  return client

# 전략 생성 함수
def generate_strategy(system_prompt: str, user_prompt: str) -> str:
    """
    vllm 모델을 통해 전략 생성을 위한 함수
    Args:
        system_prompt: 시스템 프롬프트
        user_prompt: 유저 프롬프트
    Returns:
        str: 전략
    """
    client = get_vllm()
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}],
        max_tokens=1024,
        temperature=0.1
    )
    strategy = response.choices[0].message.content
    return strategy