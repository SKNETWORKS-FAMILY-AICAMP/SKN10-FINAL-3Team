# api/views.py
from rest_framework.views import APIView
from rest_framework.exceptions import APIException
from rest_framework.response import Response 
from rest_framework import status
from django.http import StreamingHttpResponse

from rest_framework.permissions import IsAuthenticated
from user.service.jwt_auth import JWTAuthentication
from user.models import CustomUser
from user.service.token import (
    create_access_token, create_refresh_token, decode_refresh_token,
    save_refresh_token, check_refresh_token, delete_refresh_token
)
from code_t.models import Code_T
from event.models import Event
from case.models import Case
from django.shortcuts import get_list_or_404
from django.contrib.auth import login, logout
import random
from pprint import pprint

# OpenAI 클라이언트와 스트리밍 응답 함수
from llm.openai_client import stream_chat_response

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

class ChatLLMAPIView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    
    def post(self, request):
        query = request.data.get('query')
        case_ids = request.data.get('case_ids', [])

        if not query:
            return Response({"error": "query는 필수입니다."}, status=status.HTTP_400_BAD_REQUEST)

        print("[POST 요청 수신]")
        print(f"사용자 쿼리: {query}")
        print(f"선택된 판례 ID 목록: {case_ids}")

        case_data_dict = {}

        # case_ids가 있을 때만 판례 조회 수행
        if case_ids:
            cases = get_list_or_404(Case, case_id__in=case_ids)
            for idx, case in enumerate(cases, start=1):
                case_data_dict[f"case{idx}"] = {
                    "case_num": case.case_num,
                    "court_name": case.court_name,
                    "case_name": case.case_name,
                    "case_at": case.case_at.strftime("%Y-%m-%d"),
                    "decision_summary": case.decision_summary,
                    "case_full": case.case_full,
                    "decision_issue": case.decision_issue,
                    "case_result": case.case_result,
                    "refer_cases": case.refer_cases,
                    "refer_statutes": case.refer_statutes,
                    "facts_summary": case.facts_summary,
                    "facts_keywords": case.facts_keywords,
                    "issue_summary": case.issue_summary,
                    "issue_keywords": case.issue_keywords,
                    "keywords": case.keywords,
                }

        # 쿼리는 항상 포함
        case_data_dict["query"] = query

        print("📦 [LLM 전달 JSON 구조]")
        pprint(case_data_dict, indent=4, width=120)

        return StreamingHttpResponse(
            stream_chat_response(case_data_dict, query),
            content_type='text/plain; charset=utf-8-sig'
        )

