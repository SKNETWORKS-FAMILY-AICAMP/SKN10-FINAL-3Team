# user/views.py
from django.shortcuts import render

# 로그인 페이지 뷰
def login_page(request):
    response = render(request, 'user/login.html')
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response

# 프로필 페이지 뷰
def profile(request):
    return render(request, 'user/profile.html')


