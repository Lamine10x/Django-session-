from rest_framework import serializers
from .models import TicketType, Reservation
from events.serializers import EventSerializer
from users.serializers import UserSerializer

class TicketTypeSerializer(serializers.ModelSerializer):
    remaining_tickets = serializers.IntegerField(read_only=True)

    class Meta:
        model = TicketType
        fields = ['id', 'event', 'name', 'price', 'quota', 'sold_count', 'remaining_tickets']
        read_only_fields = ['id', 'sold_count']

class ReservationSerializer(serializers.ModelSerializer):
    ticket_type = TicketTypeSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Reservation
        fields = ['id', 'ticket_type', 'user', 'ticket_code', 'status', 'payment_status', 'created_at']
        read_only_fields = ['id', 'ticket_code', 'status', 'created_at']
