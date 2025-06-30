from django.core.paginator import Paginator
from django.shortcuts import render

def chatbot_view(request):
    user = request.user
    query = request.GET.get('query', '')   # query만 받는다
    page = request.GET.get('page', 1)      # 페이지네이션 유지(좌측 판례 목록 쓸 경우 대비)

    print(f"[chatbot] user : {user}")
    print(f"[chatbot] query : {query}")

    # 판례 목록: 초기에 비어있음(사용자 입력 후 챗봇 응답에서 case_ids 받아와서 JS로 갱신)
    case_data = []
    paginator = Paginator(case_data, 10)
    page_obj = paginator.get_page(page)

    context = {
        "user_name": user.name,
        "user_name_first": user.name[0],
        "query": query,
        "cases": page_obj.object_list,
        "page_obj": page_obj,
    }
    return render(request, 'chatbot/chatbot.html', context)
