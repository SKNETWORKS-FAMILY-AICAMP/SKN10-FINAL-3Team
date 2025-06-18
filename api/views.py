# api/views.py
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
from event.models import Event
from django.contrib.auth import login, logout
import random

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

# 사건 생성 및 팀 배정 API 뷰
class EventCreateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 1. 프론트엔드에서 보낸 데이터를 받습니다.
        data = request.data
        print(f"[사건 생성] 요청 데이터: {data}")
        selected_team_name = data.get('selectedTeamName', '').strip()
        print(f"[사건 생성] 선택된 팀 이름: {selected_team_name}")
        
        # 2. 선택된 팀 이름(예: "민사 1팀")으로 Code_T에서 팀 코드(예: "ORG_01_01")를 찾습니다.
        try:
            team_code_obj = Code_T.objects.get(code_label=selected_team_name)
            org_cd = team_code_obj.code
            print(f"[사건 생성] 선택된 팀 코드: {org_cd}")
            estat_code_obj = Code_T.objects.get(code=data.get('estat_cd'))
            estat_cd = estat_code_obj.code_label
            print(f"[사건 생성] 선택된 ESTAT 코드: {estat_cd}")
            
        except Code_T.DoesNotExist:
            return Response({"error": "유효하지 않은 팀 이름 or ESTAT 입니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 
        # 3. 새로운 Event 객체를 생성하고 데이터를 저장합니다.
        try:
            Event.objects.create(
                user=request.user,                      
                creator_name=request.user.name,         # 생성 시점의 이름을 텍스트로 복사
                e_title=data.get('caseTitle'),
                e_description=data.get('caseBody'),
                client=data.get('clientName'),
                cat_cd=data.get('catCd'),
                cat_02=data.get('catMid'),
                cat_03=data.get('catSub'),
                memo=data.get('caseNote'),
                org_cd=org_cd,                          
                estat_cd=estat_cd,
                lstat_cd=data.get('lstatCd'),
                estat_num_cd=data.get('estatFinalCd'),
                submit_at=data.get('retrialDate') if data.get('retrialDate') else None
            )
            return Response({"message": "사건이 성공적으로 등록되었습니다."}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            # 데이터 저장 중 발생할 수 있는 다른 모든 에러 처리
            return Response({"error": f"데이터 저장 중 오류 발생: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# 사건 조회 API 뷰
class EventListByOrgAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_org_cd = user.org_cd
        is_partner = user.is_partner

        # 파트너인 경우: 상위 부서 코드로 시작하는 모든 하위 부서 포함
        if is_partner:
            # 예: ORG_01이면 ORG_01_01, ORG_01_02 등을 포함
            matching_org_codes = Code_T.objects.filter(
                code__startswith=f"{user_org_cd}_"
            ).values_list('code', flat=True)

            matching_org_codes = list(matching_org_codes) + [user_org_cd]

        # 일반 직원인 경우: 동일한 code_label 기준으로 매칭
        else:
            try:
                user_org_label = Code_T.objects.get(code=user_org_cd).code_label
            except Code_T.DoesNotExist:
                return Response({'error': '유효하지 않은 org_cd입니다.'}, status=400)

            matching_org_codes = Code_T.objects.filter(
                code_label=user_org_label
            ).values_list('code', flat=True)

        # 사건 필터링
        events = Event.objects.filter(org_cd__in=matching_org_codes).order_by('-created_at')

        result = []
        for event in events:
            result.append({
                'event_id': event.event_id,
                'e_title': event.e_title,
                'client': event.client,
                'cat_02': event.cat_02,
                'cat_03': event.cat_03,
                'creator_name': event.creator_name,
                'estat_cd': event.estat_cd,
                'created_at': event.created_at.strftime('%Y-%m-%d')
            })

        return Response({'events': result}, status=200)