# user/urls.py
from django.urls import path
from .views import (
    RecommendTeamAPIView, EventCreateAPIView, 
    EventListByOrgAPIView
)

# API 엔드포인트 URL 구성
urlpatterns = [
    path('recommend/', RecommendTeamAPIView.as_view(), name='api-recommend'),       # 프로필 API
    path('event/create/', EventCreateAPIView.as_view(), name='api-event-create'),   # 사건 생성 API
    path('event/by-org/', EventListByOrgAPIView.as_view(), name='api-event-by-org'),# 사건 목록 조회 API

]