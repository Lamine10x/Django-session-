from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from .models import TicketType, Reservation
from .serializers import TicketTypeSerializer, ReservationSerializer
from .services import TicketService
from events.models import Event

class TicketTypeCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TicketTypeSerializer(data=request.data)
        if serializer.is_valid():
            event = serializer.validated_data['event']
            if event.organizer != request.user and not request.user.is_admin_user():
                return Response({"detail": "Non autorisé à modifier cet événement."}, status=status.HTTP_403_FORBIDDEN)
                
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TicketBookAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ticket_type_id = request.data.get('ticket_type_id')
        if not ticket_type_id:
            return Response({"detail": "ticket_type_id est requis."}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            reservation = TicketService.book_ticket(request.user, ticket_type_id)
            return Response(ReservationSerializer(reservation).data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"detail": str(e.message if hasattr(e, 'message') else e)}, status=status.HTTP_400_BAD_REQUEST)

class TicketCancelAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            reservation = TicketService.cancel_reservation(request.user, pk)
            return Response(ReservationSerializer(reservation).data)
        except ValidationError as e:
            return Response({"detail": str(e.message if hasattr(e, 'message') else e)}, status=status.HTTP_400_BAD_REQUEST)

class OrganizerDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_organizer_user() and not request.user.is_admin_user():
            return Response({"detail": "Accès réservé aux organisateurs."}, status=status.HTTP_403_FORBIDDEN)
            
        events = Event.objects.filter(organizer=request.user)
        
        dashboard_data = []
        for event in events:
            ticket_types = event.ticket_types.all()
            total_sold = sum(tt.sold_count for tt in ticket_types)
            revenue = sum(tt.sold_count * tt.price for tt in ticket_types)
            
            reservations = Reservation.objects.filter(ticket_type__event=event)
            participants = ReservationSerializer(reservations, many=True).data
            
            dashboard_data.append({
                "event_id": event.id,
                "event_title": event.title,
                "total_tickets_sold": total_sold,
                "total_revenue": float(revenue),
                "participants": participants
            })
            
        return Response(dashboard_data)
