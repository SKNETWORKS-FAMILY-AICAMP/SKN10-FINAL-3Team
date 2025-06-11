# user/urls.py
from django.urls import path
from .views import LoginView, RefreshView, Logoutview, JWTAPIView, RecommendTeamAPIView

# API 엔드포인트 URL 구성
urlpatterns = [
    path('login/', LoginView.as_view(), name='api-login'),              # 로그인 요청 처리
    path('refresh/', RefreshView.as_view(), name='api-refresh'),        # 액세스 토큰 재발급 요청
    path('logout/', Logoutview.as_view(), name='api-logout'),           # 로그아웃 요청 처리
    path('jwt/', JWTAPIView.as_view(), name='api-jwt'),                 # 프로필 API
    path('recommend/', RecommendTeamAPIView.as_view(), name='api-recommend'), # 프로필 API
]