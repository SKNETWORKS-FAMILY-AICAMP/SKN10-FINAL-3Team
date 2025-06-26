# app/services/classify_llm.py
# 쿼리 분류 및 필터 추출 서비스

import json
import re
from services.llm_handler import client

def classify_query(query: str) -> dict:
    """입력 쿼리를 조건기반 vs 유사도기반 또는 검색불가로 분류하고, 조건검색일 경우 메타데이터 기준 필터 추출"""
    prompt = f"""
당신은 판례 검색 시스템의 분류기입니다.

다음 사용자 입력이 어떤 검색 유형에 해당하는지 판별하십시오:

1. 조건기반 검색: 아래 메타데이터 필드 중 하나 이상이 명확히 포함된 경우
   - 사건번호: "2010다12345", "99나39483" 등 (숫자 + 한글 + 숫자 형식)
   - 법원명: "서울중앙지방법원", "대법원"
   - 사건명: "손해배상(자)", "대여금", "건물인도" 등 소송유형
   - 판례결과: "파기환송", "인용", "기각", "일부 인용", "각하", "조정"
   - 참조조문: "민법 제750조" 등
   - 키워드: "교통사고", "척추손상", "일실수입", "음주운전" 등 핵심 사실/쟁점

2. 유사도기반 검색: 구체적인 사례나 사건을 찾으려는 경우
   - 예: "교통사고로 인한 손해배상 사례", "부동산 계약 분쟁 판례", "근로자 부상 사건"
   - 예: "음주운전으로 인한 사망사고 판례", "건물 임대차 분쟁 사례"
   - 즉, 특정 상황이나 사건과 유사한 판례를 찾으려는 경우

3. 일반질문: 법률 개념이나 용어에 대한 설명 요청, 또는 일반적인 대화
   - 예: "손해배상이란?", "소멸시효는?", "계약이란 무엇인가요?", "안녕하세요"
   - 예: "손해배상청구권의 소멸시효는 언제인가요?" (개념 설명 요청)
   - 즉, 특정 판례를 찾는 것이 아니라 법률 지식이나 개념을 묻는 경우

※ 구분 기준:
- 유사도기반: "~사례", "~판례", "~사건" 등 구체적인 사례를 찾으려는 경우
- 일반질문: "~란?", "~는?", "~가 무엇인가요?" 등 개념이나 용어 설명을 요청하는 경우

[사용자 검색어]
"{query}"

[응답 형식 - 반드시 JSON]
{{
    "search_type": "조건기반" 또는 "유사도기반" 또는 "일반질문",
    "filters": {{
        조건기반일 경우만 해당 필드만 포함 (필요 시 일부만 포함 가능)
    }}
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "당신은 판례 검색 전문가입니다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    raw_output = response.choices[0].message.content.strip()
    print("🟡 LLM 응답 원문 ↓")
    print(raw_output)

    # ```json ... ``` 블록이 포함된 경우 JSON만 추출
    try:
        json_str = re.search(r'\{[\s\S]*\}', raw_output).group()
        return json.loads(json_str)
    except Exception as e:
        raise ValueError("❌ LLM 응답 파싱 실패:\n" + raw_output + f"\n\n[오류] {e}")
