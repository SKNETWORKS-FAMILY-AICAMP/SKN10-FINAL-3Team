from django.urls import path
from .views import chatbot_view

# http://www.localhost:8000/chatbot
urlpatterns = [
    path('', chatbot_view, name='chatbot-view'),
]
