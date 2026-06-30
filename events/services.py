from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_datetime
from .models import Event

class EventService:
    @staticmethod
    def _validate_dates(date, end_date):
        """Verifie que la date de fin est posterieure a la date de debut."""
        if not end_date:
            return
        start = date if not isinstance(date, str) else parse_datetime(date)
        end = end_date if not isinstance(end_date, str) else parse_datetime(end_date)
        if start and end and end <= start:
            raise ValidationError("La date de fin doit être postérieure à la date de début.")

    @staticmethod
    def create_event(title, description, date, location, max_capacity, organizer,
                     status=Event.DRAFT, category=Event.CONCERT, end_date=None):
        if not organizer.is_organizer_user() and not organizer.is_admin_user():
            raise ValidationError("Seuls les organisateurs peuvent créer des événements.")

        valid_categories = [choice[0] for choice in Event.CATEGORY_CHOICES]
        if category not in valid_categories:
            raise ValidationError("Catégorie d'événement invalide.")

        EventService._validate_dates(date, end_date)

        event = Event.objects.create(
            title=title,
            description=description,
            date=date,
            end_date=end_date or None,
            location=location,
            max_capacity=max_capacity,
            organizer=organizer,
            status=status,
            category=category
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
