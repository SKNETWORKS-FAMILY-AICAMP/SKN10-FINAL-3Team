# user/urls.py
from django.urls import path
from .views import (
    LoginView, Logoutview, RecommendTeamAPIView, EventCreateAPIView, 
    EventListByOrgAPIView
)

# API 엔드포인트 URL 구성
urlpatterns = [
    path('login/', LoginView.as_view(), name='api-login'),                          # 로그인 요청 처리
    path('logout/', Logoutview.as_view(), name='api-logout'),                       # 로그아웃 요청 처리
    path('recommend/', RecommendTeamAPIView.as_view(), name='api-recommend'),       # 프로필 API
    path('event/create/', EventCreateAPIView.as_view(), name='api-event-create'),   # 사건 생성 API
    path('event/by-org/', EventListByOrgAPIView.as_view(), name='api-event-by-org'),# 사건 목록 조회 API

]