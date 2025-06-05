import jwt 
import datetime 
import enum 
import pdb

from rest_framework.exceptions import AuthenticationFailed
# 토큰 설정 Enum 클래스
# - access token: 2분 (단기 사용)
# - refresh token: 2일 (장기 사용)
class JWT_KEY(enum.Enum):
    RANDOM_OF_ACCESS_KEY = (enum.auto(), 'access_secret', datetime.timedelta(seconds=120), 'HS256', '랜덤한 조합의 키')
    RANDOM_OF_REFRESH_KEY = (enum.auto(), 'refresh_secret', datetime.timedelta(days=2), 'HS256', '랜덤한 조합의 키')

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

    return jwt.encode(payload, random_key, algorithm=alg)

# 액세스 토큰 생성 함수
def create_access_token(id):
    print(f"Creating access token for user ID: {id}")  # 디버깅용
    return __create_token(id, JWT_KEY.RANDOM_OF_ACCESS_KEY)

# 리프레시 토큰 생성 함수
def create_refresh_token(id):
    return __create_token(id, JWT_KEY.RANDOM_OF_REFRESH_KEY)

# 토큰 복호화 공통 함수 (위조 여부 검증)
def __decode_token(token, key):
    try:
        alg = key.value[3]
        random_key = key.value[1]
        payload = jwt.decode(token, random_key, algorithms=alg)  # 복호화 시 위조 여부 자동 검증
        return payload['user_id']
    except Exception as e:
        raise AuthenticationFailed(e)

# 액세스 토큰 복호화 함수
def decode_access_token(token):
    return __decode_token(token, JWT_KEY.RANDOM_OF_ACCESS_KEY)

# 리프레시 토큰 복호화 함수
def decode_refresh_token(token):
    return __decode_token(token, JWT_KEY.RANDOM_OF_REFRESH_KEY)

# 인증 및 인가 흐름에서 사용:
# - 로그인 성공 시: 액세스 및 리프레시 토큰 발급
# - 요청 시: 액세스 토큰 유효성 검사
# - 토큰 만료 시: 리프레시 토큰을 사용하여 새 액세스 토큰 발급
# - 토큰 위조 시: 예외 발생 → 사용자 요청 거절

