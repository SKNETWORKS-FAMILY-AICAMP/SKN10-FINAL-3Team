# user/urls.py
from django.urls import path
from .views import login_view, logout_view

urlpatterns = [
    path('', login_view, name='user-login'),              # 로그인 페이지, 처리
    path('logout/', logout_view, name='user-logout'),     # 로그아웃 처리
]
