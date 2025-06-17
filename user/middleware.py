# user/middleware.py

from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from user.service.token import (
    decode_access_token, decode_refresh_token, create_access_token, check_refresh_token, delete_refresh_token
)
from user.models import CustomUser

# 인증이 필요 없는 URL (로그인, 리프레시 등)
EXEMPT_URLS = [
    '/', '/api/login/', '/api/refresh/', '/api/logout/', '/static/'
]

class JWTAuthRefreshMiddleware(MiddlewareMixin):
    def process_request(self, request):
        print("[🧩 Middleware] process_request 진입 >>>")
        print("[🧩 Path]", request.path)
        
        # Ajax 요청인지 검사
        if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
            return JsonResponse({'error': '잘못된 요청입니다.'}, status=400)

        # 인증이 필요 없는 URL은 패스
        if request.path in EXEMPT_URLS:
            print("[🛑 예외 URL 패스됨]", request.path)
            return None

        # 쿠키에서 JWT 토큰 읽기
        access_token = request.COOKIES.get('access_token')
        refresh_token = request.COOKIES.get('refresh_token')

        print("[🔐 access_token]", access_token[:30] if access_token else "없음")
        print("[🔐 refresh_token]", refresh_token[:30] if refresh_token else "없음")

        if not access_token:
            print("[❗] access_token 없음")
            return JsonResponse({'error': '인증 정보가 없습니다.'}, status=401)

        # access_token 디코딩
        try:
            user_id = decode_access_token(access_token)
            user = CustomUser.objects.get(id=user_id)
            request.user = user
            request._cached_user = user
            print("[✅ 유저 인증 완료] user_id:", user_id, "name:", user.name)
            
        # 토큰 만료 등 문제가 있을 경우 -> refresh_token 확인
        except Exception as e:
            print("[⚠️ access_token 예외 발생]", e)

            if refresh_token and check_refresh_token(refresh_token):
                try:
                    user_id = decode_refresh_token(refresh_token)
                    user = CustomUser.objects.get(id=user_id)
                    new_access_token = create_access_token(user_id)
                    request.user = user
                    request._cached_user = user
                    request.new_access_token = new_access_token
                    print("[♻️ 토큰 재발급 성공] user_id:", user_id, "name:", user.name)
                except Exception as inner_e:
                    print("[🧨 refresh_token도 실패]", inner_e)
                    delete_refresh_token(refresh_token)
                    resp = JsonResponse({'error': '로그인 필요'}, status=401)
                    resp.delete_cookie('access_token')
                    resp.delete_cookie('refresh_token')
                    return resp
            else:
                print("[❌ refresh_token 없음 또는 무효]")
                resp = JsonResponse({'error': '로그인 필요'}, status=401)
                resp.delete_cookie('access_token')
                resp.delete_cookie('refresh_token')
                return resp
        return None

    def process_response(self, request, response):
        # 5. 만약 새 access_token이 발급됐다면 응답에 set_cookie
        if hasattr(request, 'new_access_token'):
            response.set_cookie('access_token', request.new_access_token, httponly=True, samesite='Lax')
        return response
