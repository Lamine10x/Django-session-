from django.urls import path
from .api_views import (
    TicketTypeCreateAPIView,
    TicketBookAPIView,
    TicketCancelAPIView,
    OrganizerDashboardAPIView
)
from .views import (
    user_reservations,
    ticket_type_create,
    book_ticket_view,
    cancel_reservation_view,
    organizer_dashboard
)

urlpatterns = [
    # MVT Routes
    path('reservations/', user_reservations, name='user-reservations'),
    path('event/<int:event_pk>/ticket-type/new/', ticket_type_create, name='ticket-type-create'),
    path('ticket-type/<int:ticket_type_id>/book/', book_ticket_view, name='book-ticket'),
    path('reservation/<int:reservation_id>/cancel/', cancel_reservation_view, name='cancel-reservation'),
    path('dashboard/', organizer_dashboard, name='organizer-dashboard'),

    # API / JWT Routes
    path('api/tickets/types/', TicketTypeCreateAPIView.as_view(), name='api-ticket-type-create'),
    path('api/tickets/book/', TicketBookAPIView.as_view(), name='api-ticket-book'),
    path('api/tickets/cancel/<int:pk>/', TicketCancelAPIView.as_view(), name='api-ticket-cancel'),
    path('api/tickets/dashboard/', OrganizerDashboardAPIView.as_view(), name='api-organizer-dashboard'),
]
