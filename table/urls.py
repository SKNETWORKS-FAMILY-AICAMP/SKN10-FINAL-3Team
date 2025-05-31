from django.urls import path
from . import views

urlpatterns = [
    path('', views.table, name='table'),
    path('detail/', views.detail, name='detail'),
    path('api/documents/', views.document_list, name='document_list'),
    path('api/documents/<str:query>/', views.document_list, name='document_list_with_query'),
]
