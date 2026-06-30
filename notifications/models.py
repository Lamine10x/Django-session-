from django.db import models
from django.conf import settings

class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name="Destinataire"
    )
    message = models.CharField(max_length=255, verbose_name="Message")
    url = models.CharField(max_length=255, blank=True, verbose_name="Lien")
    is_read = models.BooleanField(default=False, verbose_name="Lue")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.username} - {self.message[:40]}"

    @classmethod
    def notify(cls, recipient, message, url=""):
        """Cree une notification pour un utilisateur."""
        if recipient is None:
            return None
        return cls.objects.create(recipient=recipient, message=message, url=url)
