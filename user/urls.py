# user/urls.py
from django.urls import path
from .views import Register, LoginView, HelloWorldView, RefreshView, Logoutview, login_page, main_page

# API 엔드포인트 URL 구성
urlpatterns = [
    path('register/', Register.as_view(), name='register'),  # 회원가입 요청 처리
    path('login/', LoginView.as_view(), name='login'),        # 로그인 요청 처리
    path('hello-world/', HelloWorldView.as_view(), name='hello-world'),  # 인증된 사용자만 접근 가능한 테스트 API
    
    path('refresh/', RefreshView.as_view(), name='refresh'),  # 액세스 토큰 재발급 요청
    path('logout/', Logoutview.as_view(), name='logout'),      # 로그아웃 요청 처리
    
    path('login-page/', login_page, name='login-page'),
    path('main-page/', main_page, name='main-page')
]