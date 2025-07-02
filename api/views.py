# api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response 
from rest_framework.permissions import IsAuthenticated
from user.service.jwt_auth import JWTAuthentication
from case.models import Case

# 판례 목록 API 뷰
class CaseListAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        case_ids = request.data.get('case_ids', [])
        if not isinstance(case_ids, list) or not case_ids:
            return Response([], status=200)

        # 문자열을 int로 변환 (에러 무시)
        int_case_ids = []
        for cid in case_ids:
            try:
                int_case_ids.append(int(cid))
            except Exception:
                continue

        if not int_case_ids:
            return Response([], status=200)

        queryset = Case.objects.filter(case_id__in=int_case_ids)
        case_map = {c.case_id: c for c in queryset}

        results = []
        for cid in int_case_ids:
            case = case_map.get(cid)
            if case is None:
                continue
            keywords = [kw.strip() for kw in (case.keywords or '').split(',') if kw.strip()]
            results.append({
                'case_id': case.case_id,
                'case_num': case.case_num,
                'case_name': case.case_name,
                'keywords': keywords,
            })
        return Response(results, status=200)