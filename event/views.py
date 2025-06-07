from django.shortcuts import render
from code_t.models import Code_T

def index(request):
    return render(request, 'event/main.html')

def write_event(request):
    cat_codes = Code_T.objects.filter(code__startswith='CAT_').order_by('code')

    estat_01_raw = Code_T.objects.filter(code__startswith='ESTAT_01_').values('code', 'code_label')
    estat_01 = [item for item in estat_01_raw if item['code'].count('_') == 2]
    estat_01_sub = [item for item in estat_01_raw if item['code'].startswith('ESTAT_01_12_')]

    estat_02_raw = Code_T.objects.filter(code__startswith='ESTAT_02_').values('code', 'code_label')
    estat_02 = [item for item in estat_02_raw if item['code'].count('_') == 2]
    estat_02_sub = [item for item in estat_02_raw if item['code'].startswith('ESTAT_02_09_')]

    lstat_codes = Code_T.objects.filter(code__startswith='LSTAT_').order_by('code')

    context = {
        'cat_codes': cat_codes,
        'estat_01': estat_01,
        'estat_02': estat_02,
        'estat_01_sub': estat_01_sub,
        'estat_02_sub': estat_02_sub,
        'lstat_codes': lstat_codes,
    }
    return render(request, 'event/write_event.html', context)


