from django.urls import path
from .api_views import EventListCreateAPIView, EventDetailAPIView
from .views import event_list, event_detail, event_create, event_edit, event_status_change

urlpatterns = [
    # MVT Routes
    path('', event_list, name='event-list'),
    path('events/<int:pk>/', event_detail, name='event-detail'),
    path('events/new/', event_create, name='event-create'),
    path('events/<int:pk>/edit/', event_edit, name='event-edit'),
    path('events/<int:pk>/status/<str:new_status>/', event_status_change, name='event-status-change'),

    # API / JWT Routes
    path('api/events/', EventListCreateAPIView.as_view(), name='api-event-list'),
    path('api/events/<int:pk>/', EventDetailAPIView.as_view(), name='api-event-detail'),
]
