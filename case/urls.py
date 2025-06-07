from django.urls import path
from .views import index, write_case

# http://www.localhost:8000/*
urlpatterns = [
    path('', index, name='case-index'),                 # http://www.localhost:8000/
    path('write/', write_case, name='case-write'),      # http://www.localhost:8000/write/
]
