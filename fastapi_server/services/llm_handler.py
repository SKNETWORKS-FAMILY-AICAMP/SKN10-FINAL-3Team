# app/services/llm_handler.py
# 공통 OpenAI 클라이언트 및 기본 LLM 함수들

from openai import OpenAI
import os
import re

# 공통 OpenAI 클라이언트
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def format_as_markdown(text: str) -> str:
    """텍스트를 마크다운 형식으로 포맷팅"""
    if not text:
        return ""
    
    # 이미 마크다운 형식인지 확인 (더 정확한 검사)
    if (text.strip().startswith('#') or 
        '**' in text or 
        '*' in text or 
        '`' in text or
        '---' in text or
        text.strip().startswith('###')):
        return text.strip()
    
    # 일반 텍스트를 마크다운으로 변환
    lines = text.strip().split('\n')
    formatted_lines = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            formatted_lines.append('')
            continue
            
        # 제목 패턴 감지 (숫자로 시작하는 경우)
        if re.match(r'^\d+\.', line):
            formatted_lines.append(f'### {line}')
        # 키워드 강조 (더 많은 키워드 추가)
        elif any(keyword in line for keyword in [
            '주요', '핵심', '중요', '결론', '요약', '쟁점', '문제', '원인', '결과',
            '법원', '판결', '인용', '기각', '파기', '환송', '승소', '패소'
        ]):
            formatted_lines.append(f'**{line}**')
        # 법조항 패턴 감지
        elif re.search(r'[가-힣]+법\s+제\d+조', line):
            # 법조항 부분만 백틱으로 감싸기
            line = re.sub(r'([가-힣]+법\s+제\d+조)', r'`\1`', line)
            formatted_lines.append(line)
        # 일반 문장
        else:
            formatted_lines.append(line)
    
    result = '\n'.join(formatted_lines)
    
    # 전체 텍스트가 너무 길면 구조화
    if len(result) > 200 and not result.startswith('#'):
        # 첫 번째 문장을 제목으로 만들기
        sentences = result.split('.')
        if sentences:
            title = sentences[0].strip()
            if title:
                result = f"### {title}\n\n{result}"
    
    return result

def ask_openai(query: str) -> str:
    """기본 OpenAI 질문-답변 함수"""
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": query}]
    )
    response = completion.choices[0].message.content.strip()
    return format_as_markdown(response)

def generate_answer(prompt: str) -> str:
    """프롬프트 기반 답변 생성 함수"""
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    response = completion.choices[0].message.content.strip()
    return format_as_markdown(response)
