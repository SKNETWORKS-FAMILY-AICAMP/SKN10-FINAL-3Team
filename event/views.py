from django.shortcuts import render
from code_t.models import Code_T

def index(request):
    print("[메인 페이지] 로그인 정보 : ", request.user)
    return render(request, 'main.html')

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



