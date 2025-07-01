from models.gpt import ask_gpt

def generate_markdown_answer(prompt: str) -> str:
    """
    마크다운 형식으로 답변 생성을 위한 함수
    Args:
        prompt: 프롬프트
    Returns:
        str: 마크다운 형식으로 답변
    """
    system_prompt = """
당신은 법률 전문가입니다.
모든 답변을 마크다운 형식으로 작성해주세요.
제목은 ###, 중요 내용은 **굵게**, 목록은 - 를 사욥하세요.
"""
    markdown_prompt = f"""{prompt}
**중요**: 반드시 마크다운 형식으로 답변해주세요.

**마크다운 형식 규칙:**
1. **제목**: ### 사용 (예: ### 주요 쟁점)
2. **강조**: **굵게** 사용 (예: **중요한 내용**)
3. **목록**: - 사용 (예: - 첫 번째 항목)
4. **법조항**: `백틱` 사용 (예: `민법 제750조`)
5. **구분선**: --- 사용 (필요시)

**답변 구조:**
- 명확한 제목으로 시작
- 중요 내용은 굵게 표시
- 목록으로 정리
- 구조화된 형태로 작성

마크다운 형식으로 답변해주세요:
"""
    response = ask_gpt(
        system_prompt=system_prompt,
        user_prompt=markdown_prompt)
    response = response.strip()
    return response