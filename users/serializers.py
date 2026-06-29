from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'first_name', 'last_name']
        read_only_fields = ['id']

# Roles autorises a l'inscription publique (ADMIN exclu volontairement).
PUBLIC_ROLE_CHOICES = [
    (User.ORGANIZER, 'Organisateur'),
    (User.PARTICIPANT, 'Participant'),
]

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=PUBLIC_ROLE_CHOICES, required=False)
