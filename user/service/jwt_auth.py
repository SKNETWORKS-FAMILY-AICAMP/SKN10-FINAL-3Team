
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from user.models import CustomUser
from .token import decode_access_token
from rest_framework.authentication import get_authorization_header
import pdb  # For debugging purposes, can be removed in production

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        print(f"[DEBUG] Raw Authorization header: {auth}")

        if not auth or auth[0].lower() != b'bearer':
            print("[DEBUG] Authorization header missing or not Bearer")
            return None

        if len(auth) == 1 or len(auth) > 2:
            raise AuthenticationFailed('Invalid token header')

        try:
            print(f"[DEBUG] Authorization header parts: {auth}")
            token = auth[1].decode('utf-8')
            
            user_id = decode_access_token(token)
            user = CustomUser.objects.get(id=user_id)
        except Exception:
            pdb.set_trace()
            raise AuthenticationFailed('Invalid token')

        return (user, None)
