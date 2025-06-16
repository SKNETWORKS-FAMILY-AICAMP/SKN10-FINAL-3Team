# user/middleware.py
# user/middleware.py

from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from user.service.token import (
    decode_access_token, decode_refresh_token, create_access_token, check_refresh_token, delete_refresh_token
)
from user.models import CustomUser

# 인증이 필요 없는 URL (로그인, 리프레시 등)
EXEMPT_URLS = [
    '/', '/api/refresh/', '/static/',
]

class JWTAuthRefreshMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # 1. 인증 예외 URL이면 미들웨어 패스
        if any(request.path.startswith(url) for url in EXEMPT_URLS):
            return None

        access_token = request.COOKIES.get('access_token')
        refresh_token = request.COOKIES.get('refresh_token')

        # 2. access_token이 없는 경우 인증 실패
        if not access_token:
            return JsonResponse({'error': '인증 정보가 없습니다.'}, status=401)

        try:
            # 3. access_token 유효성 검사
            user_id = decode_access_token(access_token)
            request.user = CustomUser.objects.get(id=user_id)
        except Exception as e:
            # access_token 만료 or 위조
            if refresh_token and check_refresh_token(refresh_token):
                # 4. refresh_token이 유효하면 새 access_token 발급
                try:
                    user_id = decode_refresh_token(refresh_token)
                    request.user = CustomUser.objects.get(id=user_id)
                    new_access_token = create_access_token(user_id)
                    request.new_access_token = new_access_token  # 응답에 추가할 플래그
                except Exception:
                    # refresh_token도 위조/만료
                    delete_refresh_token(refresh_token)
                    resp = JsonResponse({'error': '로그인 필요(토큰 만료)'}, status=401)
                    resp.delete_cookie('access_token')
                    resp.delete_cookie('refresh_token')
                    return resp
            else:
                # refresh_token 없음 or DB에서 무효(만료/로그아웃 등)
                resp = JsonResponse({'error': '로그인 필요(토큰 만료)'}, status=401)
                resp.delete_cookie('access_token')
                resp.delete_cookie('refresh_token')
                return resp

    def process_response(self, request, response):
        # 5. 만약 새 access_token이 발급됐다면 응답에 set_cookie
        if hasattr(request, 'new_access_token'):
            response.set_cookie('access_token', request.new_access_token, httponly=True, samesite='Lax')
        return response
