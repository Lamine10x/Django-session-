from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from .services import UserService
from django.contrib.auth import get_user_model

User = get_user_model()

def login_view(request):
    if request.user.is_authenticated:
        return redirect('event-list')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        selected_role = request.POST.get('role')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Les admins/superusers ne sont pas soumis au choix de role.
            if selected_role and not user.is_admin_user() and user.role != selected_role:
                messages.error(request, "Ce compte n'est pas associé au rôle sélectionné.")
                return render(request, 'users/login.html', {'roles': User.ROLE_CHOICES})

            login(request, user)
            messages.success(request, f"Bienvenue, {user.username} !")
            return redirect('event-list')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")

    return render(request, 'users/login.html', {'roles': User.ROLE_CHOICES})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('event-list')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role', User.PARTICIPANT)
        
        try:
            user = UserService.register_user(
                username=username,
                email=email,
                password=password,
                role=role
            )
            login(request, user)
            messages.success(request, "Inscription réussie !")
            return redirect('event-list')
        except ValidationError as e:
            messages.error(request, str(e.message if hasattr(e, 'message') else e))
            
    return render(request, 'users/register.html', {'roles': User.ROLE_CHOICES})

def logout_view(request):
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('login')

@login_required
def profile_edit(request):
    user = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()

        new_username = request.POST.get('username', '').strip()
        if new_username and new_username != user.username:
            if User.objects.filter(username=new_username).exclude(pk=user.pk).exists():
                messages.error(request, "Ce nom d'utilisateur est déjà pris.")
                return render(request, 'users/profile_edit.html', {'profile_user': user})
            user.username = new_username

        if request.FILES.get('photo'):
            user.photo = request.FILES['photo']

        user.save()
        messages.success(request, "Profil mis à jour avec succès !")
        return redirect('profile-edit')

    return render(request, 'users/profile_edit.html', {'profile_user': user})
