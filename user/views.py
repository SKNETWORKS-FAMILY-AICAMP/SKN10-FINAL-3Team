# user/views.py
from django.shortcuts import render
from rest_framework.views import APIView 
from rest_framework.exceptions import APIException
from rest_framework.response import Response 
from rest_framework.permissions import IsAuthenticated
from user.service.jwt_auth import JWTAuthentication
from user.models import CustomUser
from user.service.token import (
    create_access_token, create_refresh_token, decode_refresh_token,
    save_refresh_token, check_refresh_token, delete_refresh_token
)

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
    return render(request, 'user/main.html')
# 프로필 페이지 뷰
def profile(request):
    return render(request, 'user/profile.html')

# 프로필 API 뷰
class ProfileAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return Response({
            "name": user.name,
            "role": user.role,  # 권한 정보 추가
            # 추가적으로 학력, 경력 등도 필요하면 포함
        })

# 로그인 뷰
class LoginView(APIView):
    authentication_classes = []
    permission_classes = []
    
    def post(self, request):
        username = request.data['username']
        password = request.data['password']
        print(f"[로그인] 요청 - username={username}")

        # 사용자 이메일로 조회
        user = CustomUser.objects.filter(email=username).first()
        if user is None:
            print("[로그인] 사용자 없음")
            raise APIException('User not found')  # 사용자가 존재하지 않음
        elif not user.check_password(password):
            print("[로그인] 비밀번호 불일치")
            raise APIException('Incorrect password')  # 비밀번호 불일치
        print(f"[로그인] 인증 성공 - user={user.name}")

        # 토큰 생성 및 응답
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        print(f"[로그인] 토큰 발급 완료 - access_token, refresh_token")
        
        save_refresh_token(user, refresh_token)
        print(f"[로그인] refresh_token DB 저장 완료")

        response = Response({'user': user.id})
        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=False,      # 운영 환경이면 True, 개발은 False로
            samesite='Lax'
        )
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite='Lax'
        )  # 쿠키에 리프레시 토큰 저장
        
        response.data = {
            'token': access_token,  # 액세스 토큰 반환
            'user' : user.id
        }
        print(f"[로그인] 최종 응답 반환")
        return response

# 액세스 토큰 재발급 뷰
class RefreshView(APIView):
    def post(self, request):
        print("[토큰재발급] 요청 받음")
        refresh_token = request.COOKIES.get('refresh_token')
        db_token = check_refresh_token(refresh_token)
        if not db_token:
            print("[토큰재발급] 리프레시 토큰 유효성 실패")
            return Response({'error': 'Invalid or expired refresh token'}, status=401)

        user_id = decode_refresh_token(refresh_token)
        print(f"[토큰재발급] 토큰 검증 및 사용자 확인 user_id={user_id}")
        access_token = create_access_token(user_id)
        print(f"[토큰재발급] 새로운 access_token 발급")
        return Response({'token': access_token})

# 로그아웃 뷰
class Logoutview(APIView):
    def post(self, request):
        print("[로그아웃] 요청 받음")
        refresh_token = request.COOKIES.get('refresh_token')
        response = Response()
        # DB에서 해당 토큰을 찾아서 무효화
        if refresh_token:
            delete_refresh_token(refresh_token)
            print("[로그아웃] refresh_token DB 삭제 완료")
            response = Response({'message': 'success'})
            response.delete_cookie(key='refresh_token')
        print("[로그아웃] 최종 응답 반환")
        return response

# 로그인 및 인가 흐름:
# 1. 로그인 성공 시 액세스 및 리프레시 토큰 발급
# 2. 보호된 API 요청 시 액세스 토큰 유효성 검사
# 3. 토큰 만료 시 RefreshView 통해 재발급 요청
# 4. 로그아웃 시 쿠키에서 토큰 제거

