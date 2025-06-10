# user/views.py
from django.shortcuts import render

# 로그인 페이지 뷰
def login_page(request):
    response = render(request, 'user/login.html')
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response

# 메인 페이지 뷰
def main_page(request):
    # 사용자 아이디를 통해 사용자 이름 조회 후 main.html에 전달
    # request.user는 현재 로그인된 사용자 정보를 포함
    print("[메인 페이지] 진입")
    # 세션에서 확인하는 방법 -> 에세스 토큰을 열어서 확인
    # json형태로 값을 넣어야함
    return render(request, 'main.html')

# 프로필 페이지 뷰
def profile(request):
    return render(request, 'user/profile.html')


