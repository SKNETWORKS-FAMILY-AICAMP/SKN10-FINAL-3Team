# 요청 프롬프트 생성 함수
def get_request_prompt(request):
    if request.client_role == "피고":
        system_prompt = f"""다음 사건에 대한 {request.client_role} 전략을 제시해주세요.
각 양식마다 줄바꿈을 사용해주세요.
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
각 양식마다 줄바꿈을 사용해주세요.
출력 양식:
### 예상 피고 주장:
- ...
### 전략 방향성:
- ...
### 참고 자료:
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