from django.urls import path
from .views import notifications_list, notification_open

urlpatterns = [
    path('notifications/', notifications_list, name='notifications-list'),
    path('notifications/<int:pk>/open/', notification_open, name='notification-open'),
]
