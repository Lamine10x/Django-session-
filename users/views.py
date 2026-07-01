from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Sum, Count, Q
from .services import UserService
from django.contrib.auth import get_user_model

User = get_user_model()

COMMISSION_RATE = Decimal('0.10')  # 10% (modele Tikerama)

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

@login_required
def admin_dashboard(request):
    if not request.user.is_admin_user():
        messages.error(request, "Accès réservé à l'administrateur.")
        return redirect('event-list')

    # Imports locaux pour eviter les imports circulaires au chargement du module
    from events.models import Event
    from tickets.models import Reservation, Payment

    # --- Utilisateurs ---
    users_total = User.objects.count()
    users_participants = User.objects.filter(role=User.PARTICIPANT).count()
    users_organizers = User.objects.filter(role=User.ORGANIZER).count()
    users_admins = User.objects.filter(Q(role=User.ADMIN) | Q(is_superuser=True)).distinct().count()

    # --- Evenements ---
    events_total = Event.objects.count()
    events_published = Event.objects.filter(status=Event.PUBLISHED).count()
    events_draft = Event.objects.filter(status=Event.DRAFT).count()
    events_cancelled = Event.objects.filter(status=Event.CANCELLED).count()

    # --- Billetterie / finances ---
    confirmed = Reservation.objects.filter(status=Reservation.CONFIRMED)
    tickets_sold = confirmed.count()

    paid_revenue = confirmed.filter(payment_status=Reservation.PAID).aggregate(
        t=Sum('ticket_type__price'))['t'] or Decimal('0')
    pending_amount = confirmed.filter(payment_status=Reservation.PENDING).aggregate(
        t=Sum('ticket_type__price'))['t'] or Decimal('0')

    commission = (paid_revenue * COMMISSION_RATE).quantize(Decimal('1'))
    net_to_organizers = paid_revenue - commission

    # --- Top evenements par billets confirmes ---
    top_events = Event.objects.annotate(
        sold=Count('ticket_types__reservations',
                   filter=Q(ticket_types__reservations__status=Reservation.CONFIRMED))
    ).filter(sold__gt=0).order_by('-sold')[:5]

    # --- Dernieres transactions ---
    recent_payments = Payment.objects.select_related(
        'reservation__user', 'reservation__ticket_type__event'
    ).order_by('-created_at')[:8]

    context = {
        'users_total': users_total,
        'users_participants': users_participants,
        'users_organizers': users_organizers,
        'users_admins': users_admins,
        'events_total': events_total,
        'events_published': events_published,
        'events_draft': events_draft,
        'events_cancelled': events_cancelled,
        'tickets_sold': tickets_sold,
        'paid_revenue': paid_revenue,
        'pending_amount': pending_amount,
        'commission': commission,
        'net_to_organizers': net_to_organizers,
        'commission_pct': int(COMMISSION_RATE * 100),
        'top_events': top_events,
        'recent_payments': recent_payments,
    }
    return render(request, 'users/admin_dashboard.html', context)
