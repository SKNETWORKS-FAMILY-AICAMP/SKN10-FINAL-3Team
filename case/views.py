from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'case/main.html')

def write_case(request):
    return render(request, 'case/write_case.html')