from django.core.paginator import Paginator
from django.shortcuts import render
from code_t.models import Code_T
from event.models import Event

def index(request):
    user = request.user
    user_org_cd = user.org_cd
    is_partner = user.is_partner

    if is_partner:
        matching_org_codes = list(Code_T.objects.filter(
            code__startswith=f"{user_org_cd}_"
        ).values_list('code', flat=True)) + [user_org_cd]
    else:
        try:
            user_org_label = Code_T.objects.get(code=user_org_cd).code_label
            matching_org_codes = list(Code_T.objects.filter(
                code_label=user_org_label
            ).values_list('code', flat=True))
        except Code_T.DoesNotExist:
            matching_org_codes = [user_org_cd]

    # 사건 조회 및 페이지네이션
    all_events = Event.objects.filter(org_cd__in=matching_org_codes).order_by('-created_at')
    paginator = Paginator(all_events, 10)  # 한 페이지에 10건씩
    page_number = request.GET.get('page') or 1
    page_obj = paginator.get_page(page_number)

    context = {
        'user': user,
        'user_name': user.name,
        'user_name_first': user.name[0],
        'page_obj': page_obj,  # ✅ 페이지 객체 전달
    }

    return render(request, 'main.html', context)



def write_event(request):
    cat_codes = Code_T.objects.filter(code__startswith='CAT_').order_by('code')

    estat_01_raw = Code_T.objects.filter(code__startswith='ESTAT_01_').values('code', 'code_label', 'upper_code')
    estat_01 = [item for item in estat_01_raw if item['code'].count('_') == 2]

    estat_02_raw = Code_T.objects.filter(code__startswith='ESTAT_02_').values('code', 'code_label', 'upper_code')
    estat_02 = [item for item in estat_02_raw if item['code'].count('_') == 2]

    # 사건 종결 코드 자동 식별 (ex. ESTAT_01_12, ESTAT_02_09)
    estat_01_final_code = next((item['code'] for item in estat_01 if '종결' in item['code_label']), None)
    estat_02_final_code = next((item['code'] for item in estat_02 if '종결' in item['code_label']), None)

    estat_01_sub = Code_T.objects.filter(upper_code=estat_01_final_code).values('code', 'code_label') if estat_01_final_code else []
    estat_02_sub = Code_T.objects.filter(upper_code=estat_02_final_code).values('code', 'code_label') if estat_02_final_code else []

    lstat_codes = Code_T.objects.filter(code__startswith='LSTAT_').order_by('code')

    context = {
        'cat_codes': cat_codes,
        'estat_01': estat_01,
        'estat_02': estat_02,
        'estat_01_sub': list(estat_01_sub),
        'estat_02_sub': list(estat_02_sub),
        'lstat_codes': lstat_codes,
    }
    return render(request, 'event/write_event.html', context)



