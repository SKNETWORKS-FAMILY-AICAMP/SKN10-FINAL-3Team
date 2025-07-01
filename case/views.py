# cases/views.py

import re
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Case

def detail_case(request, case_id):
    user = request.user
    case = get_object_or_404(Case, case_id=case_id)

    refer_cases_list = case.refer_cases.split('/') if case.refer_cases else []
    refer_statutes_list = case.refer_statutes.split('/') if case.refer_statutes else []

    # [1], [2], ... 형식 분리
    decision_summary_list = re.split(r'(?=\[\d+\])', case.decision_summary) if case.decision_summary else []
    decision_issue_list = re.split(r'(?=\[\d+\])', case.decision_issue) if case.decision_issue else []

    # 판례 내용에서 '【' 기호 기준으로 단락 분리
    case_full_list = re.split(r'(?=【)', case.case_full) if case.case_full else []

    context = {
        'user': user,
        'user_name': user.name,
        'user_name_first': user.name[0],
        'case': case,
        'refer_cases_list': refer_cases_list,
        'refer_statutes_list': refer_statutes_list,
        'decision_summary_list': decision_summary_list,
        'decision_issue_list': decision_issue_list,
        'case_full_list': case_full_list,
    }
    return render(request, 'case/detail_case.html', context)

# FastAPI와 연동되는 JSON 응답용 API
def search_cases(request):
    filters = {}
    if court := request.GET.get("법원명"):
        filters["법원명__icontains"] = court
    if name := request.GET.get("사건명"):
        filters["사건명__icontains"] = name
    if result := request.GET.get("판례결과"):
        filters["판례결과__icontains"] = result
    if clause := request.GET.get("참조조문"):
        filters["참조조문__icontains"] = clause
    if keyword := request.GET.get("키워드"):
        filters["키워드__icontains"] = keyword

    queryset = Case.objects.filter(**filters)
    data = [
        {
            "사건번호": obj.사건번호,
            "사건명": obj.사건명,
            "법원명": obj.법원명,
            "판례결과": obj.판례결과,
            "참조조문": obj.참조조문,
            "키워드": obj.키워드,
            "요약": obj.case_full[:150] if hasattr(obj, 'case_full') else ""
        }
        for obj in queryset
    ]
    return JsonResponse(data, safe=False)
