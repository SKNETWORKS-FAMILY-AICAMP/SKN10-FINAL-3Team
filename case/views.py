import re
from django.shortcuts import render, get_object_or_404
from .models import Case

def detail_case(request, case_id):
    user = request.user
    case = get_object_or_404(Case, case_id=case_id)

    refer_cases_list = []
    if case.refer_cases and case.refer_cases.strip().lower() != 'nan':
        refer_cases_list = [
            x for x in case.refer_cases.split('/') if x.strip().lower() != 'nan'
        ]

    refer_statutes_list = []
    if case.refer_statutes and case.refer_statutes.strip().lower() != 'nan':
        refer_statutes_list = [
            x for x in case.refer_statutes.split('/') if x.strip().lower() != 'nan'
        ]

    decision_summary_list = []
    if case.decision_summary and case.decision_summary.strip().lower() != 'nan':
        decision_summary_list = [
            x for x in re.split(r'(?=\[\d+\])', case.decision_summary) if x.strip().lower() != 'nan'
        ]

    decision_issue_list = []
    if case.decision_issue and case.decision_issue.strip().lower() != 'nan':
        decision_issue_list = [
            x for x in re.split(r'(?=\[\d+\])', case.decision_issue) if x.strip().lower() != 'nan'
        ]

    case_full_list = []
    if case.case_full and case.case_full.strip().lower() != 'nan':
        case_full_list = [
            x for x in re.split(r'(?=【)', case.case_full) if x.strip().lower() != 'nan'
        ]

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