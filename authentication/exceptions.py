import re
from django.forms import ValidationError

from rest_framework.views import exception_handler

# 이메일 유효성 검사기
class EmailValidator:
    REGEX_EMAIL = r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    def __call__(self, email):
        if not re.match(self.REGEX_EMAIL, email):
            raise ValidationError("이메일 형식이 아닙니다.")

# 비밀번호 유효성 검사기
class PasswordValidator:
    REGEX_PASSWORD = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$'

    def __call__(self, password):
        if not re.match(self.REGEX_PASSWORD, password):
            raise ValidationError("비밀번호는 8자 이상이며, 영문자+숫자+특수문자를 모두 포함해야 합니다.")

# 전화번호 유효성 검사기
class PhoneNumberValidator:
    REGEX_PHONE = r'^\d{3}-\d{3,4}-\d{4}$'

    def __call__(self, phone_number):
        if not re.match(self.REGEX_PHONE, phone_number):
            raise ValidationError("전화번호 형식이 맞지 않습니다. 예: 010-1234-5678")


# 커스텀 예외 핸들러 정의
# 인증 또는 인가 과정에서 발생하는 예외에 따라 HTTP 응답 코드 수정
# -> 클라이언트는 오류 유형을 더 쉽게 구분 가능함

def status_code_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        original_code = response.status_code
        if original_code == 401:
            response.status_code = 401  # 인증 실패
        elif original_code == 403:
            response.status_code = 403  # 인가 실패
        elif original_code == 405:
            response.status_code = 405  # 메서드 미지원
        elif original_code == 400:
            response.status_code = 400  # 잘못된 요청
        else:
            response.status_code = original_code  # 나머지는 그대로
    return response

# 인가 흐름에서 사용:
# - 사용자가 잘못된 토큰을 제공하거나 인증에 실패할 경우
# - 서버는 예외를 감지하고 이 핸들러를 통해 적절한 응답 코드로 변환하여 반환