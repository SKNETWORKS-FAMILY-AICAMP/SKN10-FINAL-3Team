# user/service/jwt_auth.py
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from user.models import CustomUser
from .token import decode_access_token
from rest_framework.authentication import get_authorization_header

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # 1. 쿠키에서 access_token 먼저 꺼내기
        token = request.COOKIES.get('access_token', None)
        if not token:
            # 2. Authorization 헤더에서 Bearer 토큰 꺼내는 백업 로직
            auth = get_authorization_header(request).split()
            if not auth or auth[0].lower() != b'bearer':
                return None
            if len(auth) == 1 or len(auth) > 2:
                raise AuthenticationFailed('Invalid token header')
            try:
                token = auth[1].decode('utf-8')
            except Exception:
                raise AuthenticationFailed('Invalid token')

        try:
            user_id = decode_access_token(token)
            user = CustomUser.objects.get(id=user_id)
        except Exception:
            raise AuthenticationFailed('Invalid token')

        return (user, None)
