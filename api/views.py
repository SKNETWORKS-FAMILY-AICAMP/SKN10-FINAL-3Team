from rest_framework.views import APIView 
from rest_framework.exceptions import APIException
from rest_framework.response import Response 
from rest_framework import status

from rest_framework.permissions import IsAuthenticated
from user.service.jwt_auth import JWTAuthentication
from user.models import CustomUser
from user.service.token import (
    create_access_token, create_refresh_token, decode_refresh_token,
    save_refresh_token, check_refresh_token, delete_refresh_token
)
from code_t.models import Code_T
from django.contrib.auth import login, logout
import random

# Create your views here.
# JWT API 뷰
class JWTAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return Response({
            "name": user.name,
            "role": user.role_cd,           # 권한 정보 추가
            'is_partner': user.is_partner,  # 파트너 여부
        })

# 로그인 뷰
class LoginView(APIView):
    authentication_classes = []
    permission_classes = []
    
    def post(self, request):
        logout(request)                                 # 기존 세션 로그아웃
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

        if user.is_superuser:
            login(request, user)                        # superuser인 경우 Django 세션에 로그인
            print(f"[로그인] Superuser 세션 로그인 완료 - user={user.name}")
        
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
            'user' : user.id,
            'is_superuser': user.is_superuser,  # 관리자 여부
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

# AI 팀 추천 API 뷰
class RecommendTeamAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        category_code = request.GET.get('cat_cd', None)
        if not category_code:
            return Response({"error": "cat_cd 파라미터가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 1. 요청된 'cat_cd'로 전문가 사용자들을 필터링합니다.
        specialists = CustomUser.objects.filter(cat_cd=category_code)

        # 2. 전문가들이 속한 팀 코드(org_cd) 목록을 추출합니다.
        #    이 단계에서는 'ORG_01', 'ORG_01_01' 등이 모두 포함될 수 있습니다.
        org_codes = list(specialists.values_list('org_cd', flat=True).distinct())
        
        if not org_codes:
            return Response({"error": "해당 분류의 가용 팀을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        # 3. [수정] 실제 팀(언더바 2개) 코드만 필터링합니다.
        #    (예: ['ORG_01', 'ORG_01_01'] -> ['ORG_01_01'])
        actual_team_codes = [code for code in org_codes if code.count('_') == 2]

        if not actual_team_codes:
            return Response({"error": "해당 분류의 실제 배정 가능한 팀을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        # 4. [수정] 필터링된 실제 팀 코드만 사용하여 팀 이름을 조회합니다.
        available_team_names = list(
            Code_T.objects.filter(code__in=actual_team_codes).values_list('code_label', flat=True)
        )

        if not available_team_names:
            return Response({"error": "팀 코드에 해당하는 팀 이름을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        # 5. 팀 이름 목록에서 랜덤으로 하나를 추천팀으로 선택합니다.
        recommended_team_name = random.choice(available_team_names)
        
        # 6. 프론트엔드에 최종 결과를 반환합니다.
        response_data = {
            "recommended_team": recommended_team_name,
            "available_teams": available_team_names
        }
        return Response(response_data, status=status.HTTP_200_OK)

