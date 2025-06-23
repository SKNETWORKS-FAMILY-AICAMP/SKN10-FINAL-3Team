import re
from django.shortcuts import render, get_object_or_404
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
