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
