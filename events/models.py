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

    CONCERT = 'CONCERT'
    ONE_MAN_SHOW = 'ONE_MAN_SHOW'
    MARATHON = 'MARATHON'
    SPORT = 'SPORT'
    CHARITY = 'CHARITY'
    LEISURE = 'LEISURE'
    CULINARY = 'CULINARY'

    CATEGORY_CHOICES = [
        (CONCERT, 'Concert'),
        (ONE_MAN_SHOW, 'One Man Show'),
        (MARATHON, 'Marathon'),
        (SPORT, 'Tournoi sportif'),
        (CHARITY, 'Charité'),
        (LEISURE, 'Sortie détente'),
        (CULINARY, 'Festival culinaire'),
    ]

    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    image = models.ImageField(
        upload_to='events/',
        null=True,
        blank=True,
        verbose_name="Affiche / visuel de l'événement"
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default=CONCERT,
        verbose_name="Catégorie"
    )
    date = models.DateTimeField(verbose_name="Date et heure de début")
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date et heure de fin"
    )
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
    favorited_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='favorite_events',
        blank=True,
        verbose_name="Favori de"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
