import uuid
from django.db import models
from django.conf import settings
from events.models import Event

class TicketType(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='ticket_types',
        verbose_name="Événement"
    )
    name = models.CharField(max_length=100, verbose_name="Nom de la catégorie")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix")
    quota = models.PositiveIntegerField(verbose_name="Quota total disponible")
    sold_count = models.PositiveIntegerField(default=0, verbose_name="Nombre vendus")

    @property
    def remaining_tickets(self):
        return max(0, self.quota - self.sold_count)

    def __str__(self):
        return f"{self.event.title} - {self.name} ({self.price} FCFA)"

class Reservation(models.Model):
    CONFIRMED = 'CONFIRMED'
    CANCELLED = 'CANCELLED'
    
    STATUS_CHOICES = [
        (CONFIRMED, 'Confirmée'),
        (CANCELLED, 'Annulée'),
    ]

    PENDING = 'PENDING'
    PAID = 'PAID'
    
    PAYMENT_CHOICES = [
        (PENDING, 'En attente'),
        (PAID, 'Payé'),
    ]

    ticket_type = models.ForeignKey(
        TicketType,
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name="Type de billet"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name="Participant"
    )
    ticket_code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, verbose_name="Code unique")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=CONFIRMED,
        verbose_name="Statut réservation"
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        default=PAID,
        verbose_name="Statut paiement"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Réservation {self.ticket_code} - {self.user.username}"

class Payment(models.Model):
    WAVE = 'WAVE'
    ORANGE = 'ORANGE'
    MTN = 'MTN'
    MOOV = 'MOOV'
    CARD = 'CARD'

    METHOD_CHOICES = [
        (WAVE, 'Wave'),
        (ORANGE, 'Orange Money'),
        (MTN, 'MTN MoMo'),
        (MOOV, 'Moov Money (Flooz)'),
        (CARD, 'Carte bancaire'),
    ]

    reservation = models.OneToOneField(
        Reservation,
        on_delete=models.CASCADE,
        related_name='payment',
        verbose_name="Réservation"
    )
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, verbose_name="Moyen de paiement")
    phone_number = models.CharField(max_length=20, blank=True, verbose_name="Numéro")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant")
    reference = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, verbose_name="Référence transaction")
    is_successful = models.BooleanField(default=False, verbose_name="Paiement réussi")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Paiement {self.reference} - {self.get_method_display()} ({self.amount} FCFA)"
