from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class UserService:
    @staticmethod
    def register_user(username, email, password, role=None):
        if not username or not email or not password:
            raise ValidationError("Le nom d'utilisateur, l'email et le mot de passe sont requis.")
            
        if User.objects.filter(username=username).exists():
            raise ValidationError("Ce nom d'utilisateur est déjà pris.")
            
        if User.objects.filter(email=email).exists():
            raise ValidationError("Cet email est déjà enregistré.")
            
        if role and role not in [User.ADMIN, User.ORGANIZER, User.PARTICIPANT]:
            raise ValidationError("Rôle invalide spécifié.")
            
        role = role or User.PARTICIPANT
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role
        )
        return user
