from django.urls import path
from .views import detail_case

# http://www.localhost:8000/case
urlpatterns = [
    path('detail/<int:case_id>/', detail_case, name='case-detail'),  # http://www.localhost:8000/case/detail/1/
]
