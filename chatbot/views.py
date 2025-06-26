from django.core.paginator import Paginator
from django.shortcuts import render
from case.models import Case
import ast

def chatbot_view(request):
    user = request.user
    query = request.GET.get('query')
    ai_answer = request.GET.get('ai_answer')
    ai_case_ids_raw = request.GET.get('ai_case_ids', None)

    # 디버깅 출력
    print(f"[chatbot] user : {user}")
    print(f"[chatbot] query : {query}")
    print(f"[chatbot] ai_answer : {ai_answer}")
    print(f"[chatbot] ai_case_ids_raw : {ai_case_ids_raw}")

    page = request.GET.get('page', 1)

    # 판례 데이터 정제용 함수
    def serialize_case(case):
        keywords = case.keywords.split(',') if case.keywords else []
        return {
            'case_id': case.case_id,
            'case_num': case.case_num,
            'case_name': case.case_name,
            'keywords': [kw.strip() for kw in keywords if kw.strip()],
        }

    # 판례 목록 구성
    if ai_case_ids_raw:
        try:
            # 문자열로 받은 리스트 형태를 안전하게 파싱
            ai_case_ids = [int(cid.strip()) for cid in ai_case_ids_raw.split(',') if cid.strip().isdigit()]

            # ✅ 순서를 보장하는 조회 방식
            if isinstance(ai_case_ids, list) and ai_case_ids:
                case_qs = Case.objects.filter(case_id__in=ai_case_ids)
                case_dict = {case.case_id: case for case in case_qs}
                case_objs = [case_dict[cid] for cid in ai_case_ids if cid in case_dict]
            else:
                case_objs = []
        except Exception as e:
            print(f"[chatbot] ai_case_ids 파싱 실패: {e}")
            case_objs = []
    else:
        case_objs = []


    # 판례 직렬화 및 페이지네이션
    case_data = [serialize_case(case) for case in case_objs]
    paginator = Paginator(case_data, 10)
    page_obj = paginator.get_page(page)

    # context 구성
    context = {
        "user_name": user.name,
        "user_name_first": user.name[0],
        "query": query,
        "cases": page_obj.object_list,
        "page_obj": page_obj,
        "ai_answer": ai_answer,
    }
    if ai_case_ids_raw:
        context["ai_case_ids"] = ai_case_ids_raw

    return render(request, 'chatbot/chatbot.html', context)