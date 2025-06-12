from django.contrib import admin
from django.urls import path
from .views import index, write_event

# http://www.localhost:8000/*
urlpatterns = [
    path('', index, name='event-index'),                # http://www.localhost:8000/event/
    path('write/', write_event, name='event-write'),    # http://www.localhost:8000/event/write/
]
