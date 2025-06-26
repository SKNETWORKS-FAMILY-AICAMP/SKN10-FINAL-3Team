# app/services/embedding.py
# 텍스트 임베딩 생성 서비스

from services.llm_handler import client

def get_embedding(text: str, model="text-embedding-3-small") -> list:
    """OpenAI API를 사용해 텍스트 임베딩을 생성합니다."""
    response = client.embeddings.create(
        model=model,
        input=text
    )
    return response.data[0].embedding
