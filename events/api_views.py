from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Event
from .serializers import EventSerializer
from .services import EventService

class EventListCreateAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        if request.user.is_authenticated and (request.user.is_organizer_user() or request.user.is_admin_user()):
            events = Event.objects.filter(Q(status=Event.PUBLISHED) | Q(organizer=request.user))
        else:
            events = Event.objects.filter(status=Event.PUBLISHED)
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentification requise."}, status=status.HTTP_401_UNAUTHORIZED)
            
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            try:
                event = EventService.create_event(
                    title=serializer.validated_data['title'],
                    description=serializer.validated_data['description'],
                    date=serializer.validated_data['date'],
                    location=serializer.validated_data['location'],
                    max_capacity=serializer.validated_data['max_capacity'],
                    organizer=request.user,
                    status=serializer.validated_data.get('status', Event.DRAFT)
                )
                return Response(EventSerializer(event).data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EventDetailAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        if event.status == Event.DRAFT:
            if not request.user.is_authenticated or (request.user != event.organizer and not request.user.is_admin_user()):
                return Response({"detail": "Permission refusée pour voir ce brouillon."}, status=status.HTTP_403_FORBIDDEN)
        serializer = EventSerializer(event)
        return Response(serializer.data)

    def put(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        if request.user != event.organizer and not request.user.is_admin_user():
            return Response({"detail": "Vous n'êtes pas l'organisateur de cet événement."}, status=status.HTTP_403_FORBIDDEN)
            
        serializer = EventSerializer(event, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                new_status = serializer.validated_data.get('status')
                if new_status and new_status != event.status:
                    EventService.update_event_status(event, new_status)
                
                for attr, value in serializer.validated_data.items():
                    if attr != 'status':
                        setattr(event, attr, value)
                event.save()
                
                return Response(EventSerializer(event).data)
            except ValidationError as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        if request.user != event.organizer and not request.user.is_admin_user():
            return Response({"detail": "Vous n'êtes pas l'organisateur de cet événement."}, status=status.HTTP_403_FORBIDDEN)
            
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
