from django.db import models
from django.conf import settings

class Event(models.Model):
    DRAFT = 'DRAFT'
    PUBLISHED = 'PUBLISHED'
    CANCELLED = 'CANCELLED'
    COMPLETED = 'COMPLETED'
    
    STATUS_CHOICES = [
        (DRAFT, 'Brouillon'),
        (PUBLISHED, 'Publié'),
        (CANCELLED, 'Annulé'),
        (COMPLETED, 'Terminé'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    date = models.DateTimeField(verbose_name="Date et heure de l'événement")
    location = models.CharField(max_length=255, verbose_name="Lieu")
    max_capacity = models.PositiveIntegerField(verbose_name="Capacité maximale")
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name="Organisateur"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=DRAFT,
        verbose_name="Statut"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
