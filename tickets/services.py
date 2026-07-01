from django.db import transaction
from django.db.models import Q, F
from django.db.models.functions import Coalesce
from django.core.exceptions import ValidationError
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from events.models import Event
from notifications.models import Notification
from .models import TicketType, Reservation, Payment

class TicketService:
    @staticmethod
    def book_ticket(user, ticket_type_id, payment_status=Reservation.PAID):
        with transaction.atomic():
            try:
                ticket_type = TicketType.objects.select_for_update().get(id=ticket_type_id)
            except TicketType.DoesNotExist:
                raise ValidationError("La catégorie de billet spécifiée n'existe pas.")

            event = ticket_type.event

            if event.status != Event.PUBLISHED:
                raise ValidationError("Réservation impossible : l'événement n'est pas publié.")

            # Conflit d'agenda : un participant ne peut pas reserver deux evenements
            # DIFFERENTS dont les horaires se CHEVAUCHENT. Seules les reservations
            # CONFIRMED comptent -> annuler la concurrente libere ce creneau.
            #
            # Intervalle du nouvel evenement : [new_start, new_end[.
            # En l'absence de end_date, l'evenement est traite comme ponctuel (fin = debut).
            new_start = event.date
            new_end = event.end_date or event.date

            # Deux intervalles se chevauchent ssi  A.debut < B.fin  ET  A.fin > B.debut.
            # On ajoute l'egalite stricte des debuts pour couvrir les evenements
            # ponctuels (duree nulle) qui demarrent au meme instant.
            overlap = (
                Q(ev_start__lt=new_end, ev_end__gt=new_start)
                | Q(ev_start=new_start)
            )
            conflict_exists = (
                Reservation.objects.filter(
                    user=user,
                    status=Reservation.CONFIRMED,
                )
                .exclude(ticket_type__event=event)
                .annotate(
                    ev_start=F('ticket_type__event__date'),
                    ev_end=Coalesce(
                        'ticket_type__event__end_date',
                        'ticket_type__event__date',
                    ),
                )
                .filter(overlap)
                .exists()
            )
            if conflict_exists:
                raise ValidationError(
                    "Vous avez déjà une réservation pour un autre événement dont l'horaire chevauche celui-ci. "
                    "Annulez-la d'abord pour réserver cet événement."
                )

            # Calculate total capacity used by checking all ticket types
            total_sold = sum(tt.sold_count for tt in event.ticket_types.all())
            if total_sold >= event.max_capacity:
                raise ValidationError("La capacité maximale de l'événement a été atteinte.")

            if ticket_type.sold_count >= ticket_type.quota:
                raise ValidationError(f"Plus de billets disponibles dans la catégorie {ticket_type.name}.")

            reservation = Reservation.objects.create(
                ticket_type=ticket_type,
                user=user,
                payment_status=payment_status,
                status=Reservation.CONFIRMED
            )

            ticket_type.sold_count += 1
            ticket_type.save()

            TicketService._send_quota_notification(event)

            Notification.notify(
                user,
                f"Réservation confirmée pour « {event.title} » ({ticket_type.name}).",
                "/reservations/"
            )
            Notification.notify(
                event.organizer,
                f"Nouveau billet vendu : « {event.title} » ({ticket_type.name}).",
                "/dashboard/"
            )

            return reservation

    @staticmethod
    def cancel_reservation(user, reservation_id):
        with transaction.atomic():
            try:
                reservation = Reservation.objects.select_for_update().get(id=reservation_id)
            except Reservation.DoesNotExist:
                raise ValidationError("La réservation n'existe pas.")

            event = reservation.ticket_type.event
            if reservation.user != user and event.organizer != user and not user.is_admin_user():
                raise ValidationError("Vous n'êtes pas autorisé à annuler cette réservation.")

            if reservation.status == Reservation.CANCELLED:
                raise ValidationError("Cette réservation est déjà annulée.")

            reservation.status = Reservation.CANCELLED
            reservation.save()

            ticket_type = reservation.ticket_type
            if ticket_type.sold_count > 0:
                ticket_type.sold_count -= 1
                ticket_type.save()

            TicketService._send_quota_notification(event)

            Notification.notify(
                reservation.user,
                f"Réservation annulée pour « {event.title} ».",
                "/reservations/"
            )

            return reservation

    @staticmethod
    def process_payment(user, reservation_id, method, phone_number=""):
        """Simule un paiement Mobile Money / carte et confirme la reservation."""
        with transaction.atomic():
            try:
                reservation = Reservation.objects.select_for_update().get(id=reservation_id, user=user)
            except Reservation.DoesNotExist:
                raise ValidationError("Réservation introuvable.")

            if reservation.status == Reservation.CANCELLED:
                raise ValidationError("Cette réservation est annulée.")

            if reservation.payment_status == Reservation.PAID:
                raise ValidationError("Cette réservation est déjà payée.")

            valid_methods = [m[0] for m in Payment.METHOD_CHOICES]
            if method not in valid_methods:
                raise ValidationError("Moyen de paiement invalide.")

            # Paiement simule : toujours reussi (pas de passerelle reelle).
            payment = Payment.objects.create(
                reservation=reservation,
                method=method,
                phone_number=phone_number,
                amount=reservation.ticket_type.price,
                is_successful=True,
            )

            reservation.payment_status = Reservation.PAID
            reservation.save()

            event = reservation.ticket_type.event
            Notification.notify(
                user,
                f"Paiement confirmé ({payment.get_method_display()}) pour « {event.title} ».",
                "/reservations/"
            )
            return payment

    @staticmethod
    def _send_quota_notification(event):
        channel_layer = get_channel_layer()
        if channel_layer:
            tickets_data = [
                {
                    "ticket_type_id": tt.id,
                    "name": tt.name,
                    "remaining": tt.remaining_tickets,
                    "sold": tt.sold_count,
                    "quota": tt.quota
                }
                for tt in event.ticket_types.all()
            ]
            async_to_sync(channel_layer.group_send)(
                f"event_{event.id}",
                {
                    "type": "event_quota_update",
                    "event_id": event.id,
                    "tickets": tickets_data
                }
            )
