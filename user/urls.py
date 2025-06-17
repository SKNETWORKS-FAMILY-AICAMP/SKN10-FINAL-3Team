# user/urls.py
from django.urls import path
from .views import login_page, profile

# API 엔드포인트 URL 구성
urlpatterns = [
    path('', login_page, name='user-login-page'), # 로그인 페이지
]