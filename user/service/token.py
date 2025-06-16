# user/service/token.py
import jwt 
import datetime 
import enum 

from rest_framework.exceptions import AuthenticationFailed
from user.models import RefreshToken, CustomUser
from django.utils import timezone
# 토큰 설정 Enum 클래스
# - access token: 2분 (단기 사용)
# - refresh token: 2일 (장기 사용)
class JWT_KEY(enum.Enum):
    RANDOM_OF_ACCESS_KEY = (enum.auto(), 'access_secret', datetime.timedelta(seconds=120), 'HS256', '랜덤한 조합의 키')
    RANDOM_OF_REFRESH_KEY = (enum.auto(), 'refresh_secret', datetime.timedelta(seconds=300), 'HS256', '랜덤한 조합의 키')

# 토큰 생성 공통 함수
# - 사용자 ID를 기반으로 payload 생성 후 서명하여 토큰 발급
def __create_token(id: int, key: JWT_KEY) -> str:
    payload = {
        'user_id': id,  # 토큰에 포함된 사용자 ID
        'exp': datetime.datetime.now(tz=datetime.timezone.utc) + key.value[2],  # 만료 시간 설정
        'iat': datetime.datetime.now(tz=datetime.timezone.utc)  # 생성 시간
    }
    random_key = key.value[1]
    alg = key.value[3]
    
    print(f"[JWT] __create_token() called - id: {id}")
    return jwt.encode(payload, random_key, algorithm=alg)

# 액세스 토큰 생성 함수
def create_access_token(id):
    print(f"[JWT] create_access_token() - user ID: {id}")
    return __create_token(id, JWT_KEY.RANDOM_OF_ACCESS_KEY)

# 리프레시 토큰 생성 함수
def create_refresh_token(id):
    print(f"[JWT] create_refresh_token() - user ID: {id}")
    return __create_token(id, JWT_KEY.RANDOM_OF_REFRESH_KEY)

# 토큰 복호화 공통 함수 (위조 여부 검증)
def __decode_token(token, key):
    try:
        print(f"[JWT] __decode_token() called - key: {key.name}")
        print(f"[JWT] Decoding token (start): {str(token)[:30]}...")
        alg = key.value[3]
        random_key = key.value[1]
        payload = jwt.decode(token, random_key, algorithms=alg)  # 복호화 시 위조 여부 자동 검증
        print(f"[JWT] Decoded payload: {payload}")
        return payload['user_id']
    except Exception as e:
        print(f"[JWT] Token decoding failed: {e}")
        raise AuthenticationFailed(e)

# 액세스 토큰 복호화 함수
def decode_access_token(token):
    print(f"[JWT] decode_access_token() called")
    return __decode_token(token, JWT_KEY.RANDOM_OF_ACCESS_KEY)

# 리프레시 토큰 복호화 함수
def decode_refresh_token(token):
    print(f"[JWT] decode_refresh_token() called")
    return __decode_token(token, JWT_KEY.RANDOM_OF_REFRESH_KEY)

# DB에 리프레시 토큰 저장
def save_refresh_token(user, token):
    print(f"[토큰DB] refresh_token 저장 - user={user.email}, token={token[:10]}...")
    RefreshToken.objects.create(user=user, token=token)

# DB에서 리프레시 토큰 유효성 체크
def check_refresh_token(token):
    """
    DB에서 유효한 리프레시 토큰만 리턴.
    만료되었으면 is_valid를 False로 바꾸고 None 리턴.
    """
    print(f"[토큰DB] refresh_token 유효성 검사 - token={token[:10]}...")
    db_token = RefreshToken.objects.filter(token=token, is_valid=True).first()
    if db_token:
        # 만료일(expired_at)이 있고, 만료됐다면 무효화
        if db_token.expired_at and db_token.expired_at < timezone.now():
            db_token.is_valid = False
            db_token.save()
            return None
        print(f"[토큰DB] refresh_token 유효함")
        return db_token
    print(f"[토큰DB] 유효하지 않거나 존재하지 않음")
    return None

# DB에서 리프레시 토큰 삭제 (또는 무효화)
def delete_refresh_token(token):
    print(f"[토큰DB] refresh_token 삭제 - token={token[:10]}...")
    RefreshToken.objects.filter(token=token).delete()
    # 또는 .update(is_valid=False)로 무효화만 할 수도 있음

# 인증 및 인가 흐름에서 사용:
# - 로그인 성공 시: 액세스 및 리프레시 토큰 발급
# - 요청 시: 액세스 토큰 유효성 검사
# - 토큰 만료 시: 리프레시 토큰을 사용하여 새 액세스 토큰 발급
# - 토큰 위조 시: 예외 발생 → 사용자 요청 거절

