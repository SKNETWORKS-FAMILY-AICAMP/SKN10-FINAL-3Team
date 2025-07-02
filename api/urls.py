# user/urls.py
from django.urls import path
from .views import CaseListAPIView

# API 엔드포인트 URL 구성
urlpatterns = [
    path('case/list/', CaseListAPIView.as_view(), name='api-case-list'),  # 챗봇 판례 목록 API
]