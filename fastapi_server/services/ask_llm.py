from services.llm_handler import client #, generate_answer

def classify_ask_type(query: str) -> str:
    prompt = f"""
다음 사용자의 질문이 어떤 유형인지 분류하세요. 가능한 유형:

1. similarity: 유사한 판례들을 찾으려는 질문
   예시: "이와 비슷한 판례가 있나요?", "유사한 사례를 찾아주세요", "이런 경우의 다른 판례는?"

2. comparison: 두 판례를 비교하려는 질문  
   예시: "이 두 판례의 차이점은?", "어떤 판례가 더 유리한가?", "두 사건을 비교해주세요"

3. single_case_qa: 특정 판례 하나에 대한 질문 (가장 중요!)
   예시: "이 판례의 쟁점은?", "이 사건에서 원고가 승소한 이유는?", "이 판례의 핵심은?", 
         "이 사건의 결과는?", "이 판례의 요지는?", "이 사건의 법리는?", "이 판례의 의의는?"

4. general: 법률 개념이나 일반적인 법률 질문
   예시: "손해배상이란?", "불법행위의 요건은?", "계약의 정의는?"

질문: "{query}"

중요: "이 판례의 쟁점은?" 같은 질문은 반드시 single_case_qa로 분류하세요.

유형 (위 중 하나로만 답하세요):
"""
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    answer = completion.choices[0].message.content.strip().lower()
    if answer in ["similarity", "comparison", "single_case_qa", "general"]:
        return answer
    return "general"

def generate_markdown_answer(prompt: str) -> str:
    """마크다운 형식으로 답변 생성"""
    markdown_prompt = f"""
{prompt}

**중요**: 반드시 마크다운 형식으로 답변해주세요.

**마크다운 형식 규칙:**
1. **제목**: ### 사용 (예: ### 주요 쟁점)
2. **강조**: **굵게** 사용 (예: **중요한 내용**)
3. **목록**: - 사용 (예: - 첫 번째 항목)
4. **법조항**: - 사용 (예: - 민법 제750조)
5. **구분선**: --- 사용 (필요시)

**답변 구조:**
- 명확한 제목으로 시작
- 중요 내용은 굵게 표시
- 목록으로 정리
- 구조화된 형태로 작성

마크다운 형식으로 답변해주세요:
"""
    
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "당신은 법률 전문가입니다. 모든 답변을 마크다운 형식으로 작성해주세요. 제목은 ###, 중요 내용은 **굵게**, 목록은 - 를 사용하세요."},
            {"role": "user", "content": markdown_prompt}
        ]
    )
    response = completion.choices[0].message.content.strip()
    return response
