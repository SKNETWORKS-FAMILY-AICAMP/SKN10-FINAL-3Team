from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from user.models import CustomUser
from user.service.token import decode_access_token
from rest_framework.exceptions import AuthenticationFailed
import logging

logger = logging.getLogger('User.middleware')


class JWTAuthRefreshMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_urls = [
            '/', '/api/login/', '/api/refresh/', '/api/logout/', '/favicon.ico'
        ]

    def _redirect_to_login(self, request):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            response = JsonResponse({
                'status': 'redirect',
                'redirect_url': '/'
            }, status=401)
        else:
            response = redirect('user-login-page')

        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response

    def __call__(self, request):
        logger.info(f"[🧩 JWT 미들웨어 진입] URL: {request.path}")
        request.user = None

        if request.path in self.exempt_urls or request.path.startswith('/static/'):
            return self.get_response(request)

        access_token = request.COOKIES.get('access_token')
        refresh_token = request.COOKIES.get('refresh_token')

        if not access_token:
            logger.warning("[⚠️ access_token 없음]")
            return self._redirect_to_login(request)

        try:
            user_id = decode_access_token(access_token)
            request.user = CustomUser.objects.get(id=user_id)
            return self.get_response(request)

        except Exception as e:
            logger.warning(f"[⚠️ access_token 오류] {str(e)}")

            # refresh_token 존재 여부 확인
            if not refresh_token:
                return self._redirect_to_login(request)

            try:
                # ✅ 서버 내부에서 /api/refresh/ 호출
                from django.test import Client
                client = Client()
                client.cookies['refresh_token'] = refresh_token
                response = client.post('/api/refresh/')

                if response.status_code != 200:
                    logger.warning("[❌ 토큰 재발급 실패]")
                    return self._redirect_to_login(request)

                new_access_token = response.json().get('token')
                if not new_access_token:
                    logger.error("[❌ 응답에 access_token 없음]")
                    return self._redirect_to_login(request)

                user_id = decode_access_token(new_access_token)
                request.user = CustomUser.objects.get(id=user_id)

                response_obj = self.get_response(request)
                response_obj.set_cookie('access_token', new_access_token, httponly=True, samesite='Lax')
                logger.info(f"[♻️ 재발급 완료] user_id: {user_id}")
                return response_obj

            except Exception as inner_e:
                logger.error(f"[🧨 refresh 실패] {str(inner_e)}")
                return self._redirect_to_login(request)
