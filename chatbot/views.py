from django.core.paginator import Paginator
from django.shortcuts import render
from case.models import Case

def chatbot_view(request):
    user = request.user
    query = request.GET.get('query', '')
    page = request.GET.get('page', 1)

    # DB에서 판례 전체 조회
    case_objs = Case.objects.all()

    # 데이터 정제
    case_data = []
    for case in case_objs:
        keyword_list = case.keywords.split(',') if case.keywords else []
        keyword_list = [kw.strip() for kw in keyword_list if kw.strip()]

        case_data.append({
            'case_id': case.case_id,
            'case_num': case.case_num,
            'case_name': case.case_name,
            'keywords': keyword_list,
        })

    # 페이지네이션
    paginator = Paginator(case_data, 10)
    page_obj = paginator.get_page(page)
    
    print(f"query: {query}, page: {page}, total cases: {paginator.count}")
    
    context = {
        "user_name": user.name,
        "user_name_first": user.name[0],
        'query': query,
        'cases': page_obj.object_list,
        'page_obj': page_obj,
    }
    return render(request, 'chatbot/chatbot.html', context)
