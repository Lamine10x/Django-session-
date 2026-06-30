from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ADMIN = 'ADMIN'
    ORGANIZER = 'ORGANIZER'
    PARTICIPANT = 'PARTICIPANT'
    
    ROLE_CHOICES = [
        (ADMIN, 'Administrateur'),
        (ORGANIZER, 'Organisateur'),
        (PARTICIPANT, 'Participant'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=PARTICIPANT,
    )
    photo = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name="Photo de profil",
    )

    @property
    def initials(self):
        name = (self.first_name or self.username).strip()
        return name[0].upper() if name else "?"

    def is_admin_user(self):
        return self.role == self.ADMIN or self.is_superuser

    def is_organizer_user(self):
        return self.role == self.ORGANIZER or self.is_superuser

    def is_participant_user(self):
        return self.role == self.PARTICIPANT or self.is_superuser

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
