# user/service/token.py
import jwt 
import datetime 
import enum 

from rest_framework.exceptions import AuthenticationFailed
from user.models import RefreshToken, CustomUser
from django.utils import timezone

# 토큰 설정 Enum 클래스
# - access token: 2분 (단기 사용)
# - refresh token: 1일 (장기 사용)
class JWT_KEY(enum.Enum):
    RANDOM_OF_ACCESS_KEY = (enum.auto(), 'access_secret', datetime.timedelta(seconds=120), 'HS256', '랜덤한 조합의 키')
    RANDOM_OF_REFRESH_KEY = (enum.auto(), 'refresh_secret', datetime.timedelta(days=1), 'HS256', '랜덤한 조합의 키')

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
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed("토큰이 만료되었습니다.")
    except jwt.InvalidTokenError as e:
        raise AuthenticationFailed("유효하지 않은 토큰입니다.")

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
    expiration = timezone.now() + JWT_KEY.RANDOM_OF_REFRESH_KEY.value[2]  # 즉, 1일 후
    print(f"[토큰DB] refresh_token 저장 - user={user.email}, token={token[:10]}...")
    RefreshToken.objects.create(user=user, token=token, expired_at=expiration)

# DB에서 리프레시 토큰 삭제 (또는 무효화)
def delete_refresh_token(token):
    print(f"[토큰DB] refresh_token 삭제 - token={token[:10]}...")
    RefreshToken.objects.filter(token=token).delete()

# DB에서 리프레시 토큰 유효성 체크
def check_refresh_token(token):
    """
    DB에서 유효한 리프레시 토큰만 리턴.
    만료되었으면 is_valid=False 처리 + 로그 남기고 삭제 예약.
    """
    print(f"[토큰DB] refresh_token 유효성 검사 - token={token[:10]}...")
    db_token = RefreshToken.objects.filter(token=token, is_valid=True).first()
    if not db_token:
        print(f"[토큰DB] 유효하지 않음 or 존재하지 않음")
        return None

    now = timezone.now()
    remaining = db_token.expired_at - now

    if remaining.total_seconds() <= 0:
        # 만료된 토큰 → is_valid=False 처리 후 로그 기록
        db_token.is_valid = False
        db_token.save()
        print(f"[토큰DB] 만료된 refresh_token → is_valid=False로 무효화")
        print(f"[토큰DB] 로그: 사용자={db_token.user.email}, 만료시각={db_token.expired_at}, 삭제예정")

        # 만료된 토큰은 DB에서 삭제
        delete_refresh_token(token)
        return None

    print(f"[토큰DB] 유효한 refresh_token - 남은 시간: {remaining.total_seconds():.0f}초")
    return db_token

# access_token 재발급 로직을 캡슐화한 함수
def try_refresh_access_token(refresh_token):
    # 먼저 DB에서 유효성 체크 및 삭제/무효화 처리
    db_token = check_refresh_token(refresh_token)
    if not db_token:
        return None, None

    try:
        user_id = decode_refresh_token(refresh_token)
    except AuthenticationFailed:
        return None, None

    new_token = create_access_token(user_id)
    return new_token, user_id
