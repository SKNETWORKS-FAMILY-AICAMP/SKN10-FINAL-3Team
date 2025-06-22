from django.urls import path
from .views import index, write_event, detail_event, delete_event, edit_event

# http://www.localhost:8000/event/
urlpatterns = [
    path('', index, name='event-index'),                                # http://www.localhost:8000/event/
    path('write/', write_event, name='event-write'),                    # http://www.localhost:8000/event/write/
    path('detail/<int:event_id>/', detail_event, name='event-detail'),  # http://www.localhost:8000/event/detail/1/
    path('delete/<int:event_id>/', delete_event, name='event-delete'),  # http://www.localhost:8000/event/delete/1/
    path('edit/<int:event_id>/', edit_event, name='event-edit'),
]
