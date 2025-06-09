# user/service/jwt_auth.py
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from user.models import CustomUser
from .token import decode_access_token
from rest_framework.authentication import get_authorization_header

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != b'bearer':
            return None

        if len(auth) == 1 or len(auth) > 2:
            raise AuthenticationFailed('Invalid token header')

        try:
            token = auth[1].decode('utf-8')
            user_id = decode_access_token(token)
            user = CustomUser.objects.get(id=user_id)
        except Exception:
            raise AuthenticationFailed('Invalid token')

        return (user, None)
