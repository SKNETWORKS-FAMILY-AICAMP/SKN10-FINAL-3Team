from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from user.models import CustomUser
from user.service.token import (
    create_access_token, create_refresh_token,
    save_refresh_token, delete_refresh_token
)

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = CustomUser.objects.filter(email=email).first()

        if not user or not user.check_password(password):
            # 로그인 실패 시 로그인 페이지로 다시 렌더링 (에러 메시지 포함)
            context = {
                'error': '이메일 또는 비밀번호가 잘못되었습니다.'
            }
            return render(request, 'user/login.html', context)

        # superuser는 Django 세션 로그인도 함께 처리
        if user.is_superuser:
            login(request, user)

        # JWT 토큰 생성 및 저장
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        save_refresh_token(user, refresh_token)

        # 응답 및 쿠키 설정
        response = redirect('/admin/user/customuser/' if user.is_superuser else '/event')
        response.set_cookie('access_token', access_token, httponly=True, samesite='Lax')
        response.set_cookie('refresh_token', refresh_token, httponly=True, samesite='Lax')
        return response

    # GET 요청 시 기존 토큰 제거 + 세션 로그아웃 + DB의 refresh token도 삭제
    refresh_token = request.COOKIES.get('refresh_token')
    if refresh_token:
        delete_refresh_token(refresh_token)  # DB에서도 삭제

    logout(request)
    response = render(request, 'user/login.html')
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return response

def logout_view(request):
    if request.method == 'POST':
        # 리프레시 토큰 삭제 (DB에서도 삭제하도록 구현했다면)
        refresh_token = request.COOKIES.get('refresh_token')
        if refresh_token:
            delete_refresh_token(refresh_token)

        # Django 세션 로그아웃 (superuser였던 경우 대응)
        logout(request)

        # 쿠키 삭제 후 로그인 페이지로 리다이렉트
        response = redirect('user-login')
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response

    return redirect('user-login')