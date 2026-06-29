from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.exceptions import ValidationError
from .models import Event

class EventService:
    @staticmethod
    def create_event(title, description, date, location, max_capacity, organizer, status=Event.DRAFT):
        if not organizer.is_organizer_user() and not organizer.is_admin_user():
            raise ValidationError("Seuls les organisateurs peuvent créer des événements.")
            
        event = Event.objects.create(
            title=title,
            description=description,
            date=date,
            location=location,
            max_capacity=max_capacity,
            organizer=organizer,
            status=status
        )
        return event

    @staticmethod
    def update_event_status(event, new_status):
        old_status = event.status
        if old_status == new_status:
            return event
            
        if old_status in [Event.CANCELLED, Event.COMPLETED]:
            raise ValidationError("Impossible de modifier le statut d'un événement annulé ou terminé.")
            
        event.status = new_status
        event.save()
        
        # Send live notifications to the event WebSocket room
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"event_{event.id}",
                {
                    "type": "event_status_update",
                    "event_id": event.id,
                    "title": event.title,
                    "status": event.status,
                    "status_display": event.get_status_display(),
                }
            )
        return event
