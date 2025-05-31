from django.shortcuts import render
from django.http import JsonResponse
from test.search import main
import json

# Create your views here.
def table(request):
    return render(request, 'table/RAG_test_page.html')

def detail(request):
    return render(request, 'table/index.html')

def document_list(request):
    query = request.GET.get("query", "원심판결")
    response = main(query)
    docs = response["documents_list"]
    print(docs[0].page_content[:70], type(docs[0].page_content))
    result = []
    for idx, doc in enumerate(docs, 1):
        print(doc.page_content[:70])
        result.append({
            "no": idx,
            "사건번호": doc.metadata,
            "선고일": doc.metadata,
            "내용": doc.page_content
            # "사건번호": doc.page_content[("사건번호").encode("unicode_escape").decode("utf-8")],
            # "선고일": doc.page_content[("선고일").encode("unicode_escape").decode("utf-8")]
        })
    return JsonResponse(result, safe=False)