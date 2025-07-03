import json
import re
from models.gpt import ask_gpt
from models.response_format import generate_markdown_answer
import logging

logger = logging.getLogger(__name__)

def classify_query(query: str, context: str = "search") -> dict:
    """
    입력 쿼리를 분류하는 통합 함수
    
    Args:
        query: 사용자 쿼리
        context: 분류 컨텍스트 ("search" 또는 "qa")
    
    Returns:
        dict: 분류 결과
    """
    
    if context == "search":
        # 일반 검색 분류 (조건기반/유사도기반/일반질문)
        prompt = f"""당신은 판례 검색 시스템의 분류기입니다.

다음 사용자 입력이 어떤 검색 유형에 해당하는지 판별하십시오:

1. 조건기반 검색: 아래 메타데이터 필드 중 하나 이상이 명확히 포함된 경우
    - 사건번호: "2010다12345", "99나39483" 등 (숫자 + 한글 + 숫자 형식)
    - 법원명: "서울중앙지방법원", "대법원" 등 법원명
    - 사건명: "손해배상(자)", "대여금", "건물인도" 등 소송유형 
    - 판례결과: "파기환송", "인용", "기각", "일부 인용", "각하", "조정" 등 판례결과
    - 참조조문: "민법 제750조" 등 참조조문

2. 유사도기반 검색: 구체적인 사례나 사건을 찾으려는 경우
    - 예: "교통사고로 인한 손해배상 사례", "부동산 계약 분쟁 판례", "근로자 부상 사건"
    - 예: "음주운전으로 인한 사망사고 판례", "건물 임대차 분쟁 사례"
    - 즉, 특정 상황이나 사건과 유사한 판례를 찾으려는 경우

3. 일반질문: 법률 개념이나 용어에 대한 설명 요청, 또는 일반적인 대화
    - 예: "손해배상이란?", "소멸시효는?", "계약이란 무엇인가요?", "안녕하세요"
    - 예: "손해배상청구권의 소멸시효는 언제인가요?" (개념 설명 요청)
    - 즉, 특정 판례를 찾는 것이 아니라 법률 지식이나 개념을 묻는 경우

※ 구분 기준:
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
    else:
        # 특정 판례 질문 분류 (단일판례질문/판례비교/유사도검색/일반질문)
        prompt = f"""
다음 사용자의 질문이 어떤 유형인지 분류하세요. 가능한 유형:

1. 조건기반: 판례의 RDB 데이터(법원명, 사건명, 판례결과, 사건번호, 참조조문)로 특정 조건을 지정해 판례를 찾으려는 질문
    예시: 
      - "대법원에서 손해배상(자) 사건 중에 인용된 판례 알려줘"
      - "서울중앙지방법원 2020가합12345 판례 알려줘"
      - "민법 제750조가 적용된 판례 찾아줘"
      - "교통사고로 인한 손해배상 판례 중 기각된 사례 알려줘"

2. single_case_qa: 특정 판례 하나에 대한 질문 (가장 중요!)
    예시: "이 판례의 쟁점은?", "이 사건에서 원고가 승소한 이유는?", "이 판례의 핵심은?", "이 사건의 결과는?", "이 판례의 요지는?", "이 사건의 법리는?", "이 판례의 의의는?"

3. comparison: 두 판례를 비교하려는 질문  
    예시: "이 두 판례의 차이점은?", "어떤 판례가 더 유리한가?", "두 사건을 비교해주세요"

4. similarity: 유사한 판례들을 찾으려는 질문
    예시: "이와 비슷한 판례가 있나요?", "유사한 사례를 찾아주세요", "이런 경우의 다른 판례는?"

5. general: 법률 개념이나 일반적인 법률 질문
    예시: "손해배상이란?", "불법행위의 요건은?", "계약의 정의는?"

질문: "{query}"

중요: 
- 판례의 조건(법원명, 사건명, 판례결과, 사건번호, 참조조문, 키워드 등)이 명확히 포함된 검색은 반드시 조건기반으로 분류하세요.
- "이 판례의 쟁점은?" 같은 질문은 반드시 single_case_qa로 분류하세요.

[응답 형식 - 반드시 JSON]
{{
    "ask_type": "조건기반" 또는 "single_case_qa" 또는 "comparison" 또는 "similarity" 또는 "general"
}}
"""
    response = ask_gpt(
        system_prompt="당신은 판례 검색 전문가입니다.",
        user_prompt=prompt)
    logger.info(f"🟡 LLM 응답 원문 ↓")
    logger.info(response)
    raw_output = response.strip().lower()

    # ```json ... ``` 블록이 포함된 경우 JSON만 추출
    try:
        json_str = re.search(r'\{[\s\S]*\}', raw_output).group()
        return json.loads(json_str)
    except Exception as e:
        raise ValueError("❌ LLM 응답 파싱 실패:\n" + raw_output + f"\n\n[오류] {e}")

def classify_ask_type(query: str) -> str:
    """특정 판례에 대한 질문 유형 분류 (하위 호환성을 위해 유지)"""
    result = classify_query(query, context="qa")
    return result.get("ask_type", "general")

def ask_llm(query: str, case_ids: list, search_type: str = "일반질문") -> str:
    """
    query와 case_ids를 받아서 LLM 답변 생성
    
    Args:
        query: 사용자 질문
        case_ids: 판례 ID 리스트
        search_type: 검색 유형 (조건기반/유사도기반/일반질문)

    Returns:
        str: LLM 응답
    """
    # 조건 기반 검색일 때는 간단한 답변만
    if search_type == "조건기반":
        if not case_ids:
            return "조건에 맞는 판례를 찾지 못했습니다."
        else:
            return f"조건에 맞는 판례 {len(case_ids)}건을 찾았습니다."
    
    # 유사도 기반 검색일 때도 간단한 답변만
    if search_type == "유사도기반":
        if not case_ids:
            return "유사한 판례를 찾지 못했습니다."
        else:
            return f"유사한 판례 {len(case_ids)}건을 찾았습니다."
    
    if not case_ids:
        # case_ids가 없으면 일반 질문으로 처리
        prompt = f"""
다음 질문에 대해 간단하고 명확하게 답변해 주세요.
법률 관련 질문이면 법률적 관점에서, 일반적인 질문이면 일반적인 관점에서 답변해 주세요.

[질문]
{query}

답변:
"""
        response = ask_gpt(
            system_prompt="당신은 법률 전문가입니다.",
            user_prompt=prompt)
        return response.strip()
    
    else:
        # case_ids가 있으면 해당 판례들을 참조하여 답변 (일반질문인 경우만)
        from rds_query import get_case_by_id
        
        cases_info = ""
        for i, case_id in enumerate(case_ids):
            case_data = get_case_by_id(int(case_id))
            if case_data:
                cases_info += f"\n[판례{i+1} 정보]\n"
                for key, value in case_data.items():
                    if value:
                        cases_info += f"{key}: {value}\n"
        
        prompt = f"""
다음 질문에 대해 제공된 판례 정보를 바탕으로 답변해 주세요.

[질문]
{query}

{cases_info}

답변:
"""
        response = ask_gpt(
            system_prompt="당신은 법률 전문가입니다. 제공된 판례 정보를 바탕으로 정확하고 유용한 답변을 제공해주세요.",
            user_prompt=prompt)
        response = generate_markdown_answer(response)
        return response.strip()
