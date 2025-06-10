# user/urls.py
from django.urls import path
from .views import login_page, profile

# API 엔드포인트 URL 구성
urlpatterns = [
    path('login/', login_page, name='login-page'), # 로그인 페이지
    path('profile/', profile, name='profile'),  # 프로필 페이지
]