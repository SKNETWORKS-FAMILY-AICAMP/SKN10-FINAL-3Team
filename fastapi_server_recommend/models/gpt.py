from openai import OpenAI
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# gpt 클라이언트 호출 함수
def get_gpt() -> OpenAI:
  client = OpenAI(api_key=OPENAI_API_KEY)
  return client

# gpt 모델 응답 함수
def ask_gpt(system_prompt: str, user_prompt: str, model: str = "gpt-4o", temperature: float = 0.3) -> str:
  """
  Args:
    system_prompt: 시스템 프롬프트
    user_prompt: 유저 프롬프트
    model: 모델 이름 (Default: gpt-4o)
    temperature: 온도 (Default: 0.3)
  Returns:
    str: 응답 내용
  """
  client = get_gpt()
  
  messages = []
  
  # system_prompt가 존재하고 비어있지 않을 경우에만 추가
  if system_prompt and system_prompt.strip():
    messages.append({"role": "system", "content": system_prompt})
  
  messages.append({"role": "user", "content": user_prompt})
  
  response = client.chat.completions.create(
    model=model,
    messages=messages,
    temperature=temperature
  )
  return response.choices[0].message.content

# gpt embedding 응답 함수
def get_embedding(text: str, model: str = "text-embedding-3-small") -> list[float]:
  """
  Args:
    text: 텍스트
    model: 모델 이름 (Default: text-embedding-3-small)
  Returns:
    list[float]: 임베딩 벡터
  """
  client = get_gpt()
  response = client.embeddings.create(
    model=model,
    input=text
  )
  return response.data[0].embedding