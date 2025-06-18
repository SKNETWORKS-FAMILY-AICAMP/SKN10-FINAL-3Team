# user/urls.py
from django.urls import path
from .views import (
    RecommendTeamAPIView
)

# API 엔드포인트 URL 구성
urlpatterns = [
    path('recommend/', RecommendTeamAPIView.as_view(), name='api-recommend'),       # 추천 API

]