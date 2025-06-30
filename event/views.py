from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from code_t.models import Code_T
from event.models import Event
import math

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

    # 사건 최신순 정렬
    all_events = Event.objects.filter(org_cd__in=matching_org_codes).order_by('-created_at')

    # 진행상태 label 매핑
    estat_code_map = {
        code.code: code.code_label for code in Code_T.objects.filter(code__startswith='ESTAT_')
    }
    for event in all_events:
        event.estat_label = estat_code_map.get(event.estat_cd, event.estat_cd)

    # 페이지네이션
    paginator = Paginator(all_events, 10)
    page_number = request.GET.get('page') or 1
    page_obj = paginator.get_page(page_number)

    # 번호 계산 및 zip 처리
    total_count = all_events.count()
    page_number_int = int(page_number)
    start_index = total_count - ((page_number_int - 1) * paginator.per_page)

    # 번호와 객체를 튜플로 묶어서 넘김
    page_with_numbers = list(zip(
        range(start_index, start_index - len(page_obj), -1),
        page_obj
    ))

    context = {
        'user': user,
        'user_name': user.name,
        'user_name_first': user.name[0],
        'page_obj': page_obj,
        'page_with_numbers': page_with_numbers,  # ✅ 새로 추가된 리스트
    }
    
    return render(request, 'main.html', context)


def write_event(request):
    if request.method == 'POST':
        user = request.user

        # 1. POST 데이터 수집
        case_title = request.POST.get('case_title')
        client_name = request.POST.get('client_name')
        client_role = request.POST.get('client_role')
        cat_cd = request.POST.get('cat_cd')
        cat_mid = request.POST.get('cat_mid') or None
        e_description = request.POST.get('e_description')
        estat_cd = request.POST.get('estat_cd')
        lstat_cd = request.POST.get('lstat_cd') or None
        estat_final_cd = request.POST.get('estat_final_cd') or None
        retrial_date = request.POST.get('retrial_date') or None
        case_note = request.POST.get('case_note') or None
        team_name = request.POST.get('selected_team_name')
        ai_strategy = request.POST.get('ai_strategy') or ''
        
        event_num = request.POST.get('event_num') or None
        claim_summary = request.POST.get('claim_summary')
        event_file = request.POST.get('event_file') or None

        # 줄바꿈을 마크다운 문단 구분용으로 변환
        ai_strategy_cleaned = ai_strategy.replace('\r\n', '\n').replace('\r', '\n')
        
        # 2. 날짜 변환
        retrial_dt = None
        if retrial_date:
            try:
                retrial_dt = timezone.datetime.strptime(retrial_date, "%Y-%m-%d")
            except ValueError:
                retrial_dt = None

        # 3. team_name(label)에 해당하는 code 값을 org_cd로 조회
        try:
            org_code = Code_T.objects.get(code_label=team_name).code
        except Code_T.DoesNotExist:
            org_code = None  # 또는 예외처리

        # 4. Event 저장
        Event.objects.create(
            user=user,
            creator_name=user.name,
            e_title=case_title,
            client=client_name,
            client_role = client_role,
            cat_cd=cat_cd,
            cat_02=cat_mid,
            e_description=e_description,
            estat_cd=estat_cd,
            lstat_cd=lstat_cd,
            estat_num_cd=estat_final_cd,
            submit_at=retrial_dt,
            memo=case_note,
            org_cd=org_code,
            ai_strategy=ai_strategy_cleaned,
            
            event_num=event_num,
            claim_summary=claim_summary,
            event_file=event_file,
        )

        return redirect('/event')
    
    user = request.user
    
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
        'user': user,
        'user_name': user.name,
        'user_name_first': user.name[0],
        'cat_codes': cat_codes,
        'estat_01': estat_01,
        'estat_02': estat_02,
        'estat_01_sub': list(estat_01_sub),
        'estat_02_sub': list(estat_02_sub),
        'lstat_codes': lstat_codes,
    }
    return render(request, 'event/write_event.html', context)

def detail_event(request, event_id):
    event = get_object_or_404(Event, event_id=event_id)

    # 코드 → 라벨 매핑
    def get_label(code):
        try:
            if code is None or str(code).lower() == 'nan' or (isinstance(code, float) and math.isnan(code)):
                return None
            return Code_T.objects.get(code=code).code_label
        except Code_T.DoesNotExist:
            return None

    # 라벨 정보 추가
    event.org_label = get_label(event.org_cd)
    event.cat_label = get_label(event.cat_cd)
    event.estat_label = get_label(event.estat_cd)
    event.lstat_label = get_label(event.lstat_cd) if event.lstat_cd else "미정"
    event.estat_num_label = get_label(event.estat_num_cd) if event.estat_num_cd else "사건 진행중"

    context = {
        "event": event,
        "user_name": request.user.name,
        "user_name_first": request.user.name[0],
        'is_partner': request.user.is_partner,
    }
    return render(request, 'event/detail_event.html', context)

# 사건 삭제
def delete_event(request, event_id):
    event = get_object_or_404(Event, event_id=event_id)
    
    event.delete()
    
    return redirect('/event')

def edit_event(request, event_id):
    event = get_object_or_404(Event, event_id=event_id)
    
    if request.method == 'POST':
        # 1. 데이터 수집
        client_name = request.POST.get('client_name')
        e_description = request.POST.get('e_description')
        estat_cd = request.POST.get('estat_cd')
        lstat_cd = request.POST.get('lstat_cd') or None
        estat_final_cd = request.POST.get('estat_final_cd') or None
        retrial_date = request.POST.get('retrial_date') or None
        case_note = request.POST.get('case_note') or None
        
        event_num = request.POST.get('event_num') or None
        claim_summary = request.POST.get('claim_summary')
        event_file = request.POST.get('event_file') or None
        ai_strategy = "AI가 전략을 분석하고 있습니다. 잠시만 기다려주세요."

        # 2. 날짜 변환
        retrial_dt = None
        if retrial_date:
            try:
                retrial_dt = timezone.datetime.strptime(retrial_date, "%Y-%m-%d")
            except ValueError:
                retrial_dt = None

        # 3. 필드 업데이트
        event.client = client_name
        event.e_description = e_description
        event.estat_cd = estat_cd
        event.lstat_cd = lstat_cd
        event.estat_num_cd = estat_final_cd
        event.submit_at = retrial_dt
        event.memo = case_note
        
        event.event_num = event_num
        event.claim_summary = claim_summary
        event.event_file = event_file
        event.ai_strategy = ai_strategy

        event.save()

        return redirect('event-detail', event_id=event.event_id)

    user = request.user
    
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
        'user': user,
        'user_name': user.name,
        'user_name_first': user.name[0],
        'cat_codes': cat_codes,
        'estat_01': estat_01,
        'estat_02': estat_02,
        'estat_01_sub': list(estat_01_sub),
        'estat_02_sub': list(estat_02_sub),
        'lstat_codes': lstat_codes,
        'event': event,
    }
    return render(request, 'event/edit_event.html', context)