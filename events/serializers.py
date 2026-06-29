from rest_framework import serializers
from .models import Event
from users.serializers import UserSerializer

class EventSerializer(serializers.ModelSerializer):
    organizer = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'date', 'location', 'max_capacity', 'status', 'status_display', 'organizer', 'created_at', 'updated_at']
        read_only_fields = ['id', 'organizer', 'created_at', 'updated_at']
