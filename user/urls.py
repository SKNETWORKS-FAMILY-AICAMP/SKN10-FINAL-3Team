# user/urls.py
from django.urls import path
from .views import LoginView, RefreshView, Logoutview, ProfileAPIView, login_page, main_page, profile

# API 엔드포인트 URL 구성
urlpatterns = [
    path('api/login/', LoginView.as_view(), name='login'),  # 로그인 요청 처리
    path('refresh/', RefreshView.as_view(), name='refresh'),  # 액세스 토큰 재발급 요청
    path('logout/', Logoutview.as_view(), name='logout'),      # 로그아웃 요청 처리
    path('api/profile/', ProfileAPIView.as_view(), name='profile-api'),  # 프로필 API
    
    path('login/', login_page, name='login-page'), # 로그인 페이지
    path('main-page/', main_page, name='main-page'), # 메인 페이지
    path('profile/', profile, name='profile'),  # 프로필 페이지
]