from django.shortcuts import render

# Create your views here.
def chatbot_view(request):
    user = request.user
    
    context = {
        "user_name": request.user.name,
        "user_name_first": request.user.name[0],
    }
    return render(request, 'chatbot/chatbot.html', context)