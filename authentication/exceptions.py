from rest_framework.views import exception_handler 

# 커스텀 예외 핸들러 정의
# 인증 또는 인가 과정에서 발생하는 예외에 따라 HTTP 응답 코드 수정
# -> 클라이언트는 오류 유형을 더 쉽게 구분 가능함

def status_code_handler(exc, context):
    response = exception_handler(exc, context)  # 기본 예외 처리 수행

    if response is not None:
        response.status_code = 777  # 예외가 발생했지만 사용자 정의 처리된 경우 사용자 지정 코드 반환
    elif response.status_code >= 400 and response.status_code < 500:
        response.status_code = 444  # 클라이언트 측 오류 처리
    elif response.status_code >= 500:
        response.status_code = 555  # 서버 측 오류 처리

    return response

# 인가 흐름에서 사용:
# - 사용자가 잘못된 토큰을 제공하거나 인증에 실패할 경우
# - 서버는 예외를 감지하고 이 핸들러를 통해 적절한 응답 코드로 변환하여 반환