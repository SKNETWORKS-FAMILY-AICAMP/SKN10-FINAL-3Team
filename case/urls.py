# cases/urls.py

from django.urls import path
from .views import detail_case, search_cases

urlpatterns = [
    # 기존 상세 조회 페이지용 URL
    path("detail/<str:case_id>/", detail_case, name="case_detail"),

    # FastAPI 연동용 조건기반 검색 API
    path("search", search_cases, name="case_search"),
]
