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
    return render(request, 'user/login.html')
# 메인 페이지 뷰
def main_page(request): # 사용자 아이디를 통해 사용자 이름 조회 후 main.html에 전달
    # request.user는 현재 로그인된 사용자 정보를 포함
    print("[메인 페이지] 요청 받음")
    print(f"[메인 페이지] 요청 사용자: {request.user}")
    return render(request, 'user/main.html', {
        'user_name': request.user
    })
# 프로필 페이지 뷰
def profile(request):
    return render(request, 'user/profile.html')

# 프로필 API 뷰
class ProfileAPIView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return Response({
            "name": user.name,
            "email": user.email,
            # 추가적으로 학력, 경력 등도 필요하면 포함
        })
        
# 로그인 뷰
class LoginView(APIView):
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
        print(f"[로그인] RefreshToken DB 저장 완료")

        response = Response()
        response.set_cookie(key='refreshToken', value=refresh_token, httponly=True)  # 쿠키에 리프레시 토큰 저장
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
        refresh_token = request.COOKIES.get('refreshToken')
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
        refresh_token = request.COOKIES.get('refreshToken')
        response = Response()
        # DB에서 해당 토큰을 찾아서 무효화
        if refresh_token:
            delete_refresh_token(refresh_token)
            print("[로그아웃] RefreshToken DB 삭제 완료")
            response = Response({'message': 'success'})
            response.delete_cookie(key='refreshToken')
        print("[로그아웃] 최종 응답 반환")
        return response

# 로그인 및 인가 흐름:
# 1. 로그인 성공 시 액세스 및 리프레시 토큰 발급
# 2. 보호된 API 요청 시 액세스 토큰 유효성 검사
# 3. 토큰 만료 시 RefreshView 통해 재발급 요청
# 4. 로그아웃 시 쿠키에서 토큰 제거

