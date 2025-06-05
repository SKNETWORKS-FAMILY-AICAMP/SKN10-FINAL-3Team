# user/views.py
from django.shortcuts import render

from rest_framework.authentication import get_authorization_header
from rest_framework.views import APIView 
from rest_framework.response import Response 
from rest_framework.exceptions import AuthenticationFailed , APIException
from rest_framework.permissions import IsAuthenticated

from user.models import CustomUser
from user.serializer import UserSerializer
from user.service.token import create_access_token, create_refresh_token, decode_refresh_token

# 로그인 페이지 뷰
def login_page(request):
    return render(request, 'user/login.html')
# 메인 페이지 뷰
def main_page(request):
    return render(request, 'user/mainpage.html')

# 회원가입 뷰
class Register(APIView):
    def post(self, request):
        print(f"request : {request}")  # 요청 객체 출력 (디버깅 용도)
        print(f"request.data : {request.data}")  # 요청 데이터 출력 (디버깅 용도)
        # 사용자 데이터 직렬화 및 유효성 검사
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()  # 사용자 DB 저장
        return Response(serializer.data)

# 로그인 뷰
class LoginView(APIView):
    def post(self, request):
        username = request.data['username']
        password = request.data['password']

        # 사용자 이메일로 조회
        user = CustomUser.objects.filter(email=username).first()
        if user is None:
            raise APIException('User not found')  # 사용자가 존재하지 않음
        elif not user.check_password(password):
            raise APIException('Incorrect password')  # 비밀번호 불일치
        
        # 토큰 생성 및 응답
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        response = Response()
        response.set_cookie(key='refreshToken', value=refresh_token, httponly=True)  # 쿠키에 리프레시 토큰 저장
        response.data = {
            'token': access_token,  # 액세스 토큰 반환
            'user': user.name
        }
        return response

# 인증된 사용자만 접근 가능한 API 뷰
class HelloWorldView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        print(f"User: {request.user}")
        print(f"Is Authenticated: {request.user.is_authenticated}")
        print(f"Is Active: {request.user.is_active}")
        content = {
                "message": "Hello World",
            }
        
        return Response(content)

# 액세스 토큰 재발급 뷰
class RefreshView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get('refreshToken')  # 클라이언트 쿠키에서 토큰 추출
        id = decode_refresh_token(refresh_token)  # 리프레시 토큰 복호화 및 검증
        access_token = create_access_token(id)  # 새로운 액세스 토큰 발급
        return Response({
            'token': access_token 
        })

# 로그아웃 뷰
class Logoutview(APIView):
    def post(self, _):
        response = Response()
        response.delete_cookie(key='refreshToken')  # 쿠키에서 리프레시 토큰 제거
        response.data = {
            'message': 'success'
        }
        return response

# 로그인 및 인가 흐름:
# 1. 로그인 성공 시 액세스 및 리프레시 토큰 발급
# 2. 보호된 API 요청 시 액세스 토큰 유효성 검사
# 3. 토큰 만료 시 RefreshView 통해 재발급 요청
# 4. 로그아웃 시 쿠키에서 토큰 제거

