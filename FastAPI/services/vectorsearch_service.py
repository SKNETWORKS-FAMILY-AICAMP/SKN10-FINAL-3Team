# services/vectorsearch_service.py

import re
from openai import OpenAI
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

# ✅ .env 로드 & OpenAI 초기화
load_dotenv()
client = OpenAI()

# ✅ 벡터DB 로드
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vector_db = FAISS.load_local(
    "faiss_event_db",
    embeddings,
    allow_dangerous_deserialization=True
)


def gpt_summarize(text: str) -> str:
    """
    사건 설명문을 LLM으로 요약하여 핵심 문장 2~3개 발췌
    """
    prompt = f"""
    다음은 민사소송 사건의 설명입니다.

    - 이 설명에서 **사건의 주요 흐름과 쟁점, 당사자 주장, 사실관계**를 가장 잘 드러내는 핵심 문장 2~3개만 골라주세요.
    - 반드시 **원문에서 발췌된 구체적 설명 문장**만 사용하세요.
    - 각 문장은 사건을 이해하는 데 도움이 되어야 하며, 단순 키워드가 아닌 **사건의 맥락**을 보여주는 설명이어야 합니다.
    - 각 문장은 텍스트로만 이루어져야 합니다.

    사건 설명:
    {text}

    핵심 문장 2~3개:
    """.strip()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


def clean_numbering_and_quotes_to_inline(text: str) -> str:
    """
    LLM 요약문에서 번호, 큰따옴표 제거 후 문장들을 한 줄로 연결
    """
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        line = re.sub(r'^\s*\d+\.\s*', '', line).strip()
        if line.startswith('"') and line.endswith('"'):
            line = line[1:-1].strip()
        if line:
            cleaned.append(line)

    # 한 줄에 여러 문장 있으면 분리
    if len(cleaned) == 1 and cleaned[0].count('"') >= 2:
        matches = re.findall(r'"([^"]+)"', cleaned[0])
        cleaned = [m.strip() for m in matches if m.strip()]

    # 각 문장 끝 마침표 붙이기
    cleaned = [s if s.endswith('.') else s + '.' for s in cleaned]
    return ' '.join(cleaned)


async def vector_search(query: str, threshold: float = 1.15, k: int = 20):
    """
    1) GPT로 요약 + 전처리 → 벡터 DB 검색 → 상위 문서 반환
    """
    print("\n[VectorSearch] 원본 쿼리:", query)

    preprocessed_query = gpt_summarize(query)
    prepro_query = clean_numbering_and_quotes_to_inline(preprocessed_query)

    print("[VectorSearch] 요약:", preprocessed_query)
    print("[VectorSearch] 전처리:", prepro_query)

    results_with_score = vector_db.similarity_search_with_score(
        prepro_query, k=k
    )
    results_sorted = sorted(results_with_score, key=lambda x: x[1])

    top_event_ids = []
    for doc, score in results_sorted:
        if score > threshold:
            continue
        event_num = doc.metadata.get("event_num")
        top_event_ids.append({event_num: score})

    print("\n[VectorSearch] top_event_ids:", top_event_ids)
    return top_event_ids
