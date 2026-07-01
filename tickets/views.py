from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from events.models import Event
from .models import TicketType, Reservation, Payment
from .services import TicketService

@login_required
def user_reservations(request):
    reservations = Reservation.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'tickets/user_reservations.html', {'reservations': reservations})

@login_required
def ticket_type_create(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk)
    if request.user != event.organizer and not request.user.is_admin_user():
        messages.error(request, "Vous n'êtes pas l'organisateur de cet événement.")
        return redirect('event-detail', pk=event.pk)
        
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        quota = request.POST.get('quota')
        
        try:
            TicketType.objects.create(
                event=event,
                name=name,
                price=price,
                quota=quota
            )
            messages.success(request, f"Catégorie '{name}' ajoutée avec succès.")
            return redirect('event-detail', pk=event.pk)
        except Exception as e:
            messages.error(request, f"Erreur lors de la création : {e}")
            
    return render(request, 'tickets/ticket_type_form.html', {'event': event})

@login_required
def book_ticket_view(request, ticket_type_id):
    ticket_type = get_object_or_404(TicketType, pk=ticket_type_id)
    if request.method == 'POST':
        try:
            # La reservation est creee EN ATTENTE de paiement.
            reservation = TicketService.book_ticket(
                request.user, ticket_type.id, payment_status=Reservation.PENDING
            )
            messages.info(request, "Réservation enregistrée. Finalisez le paiement pour confirmer votre billet.")
            return redirect('payment', reservation_id=reservation.id)
        except ValidationError as e:
            messages.error(request, str(e.message if hasattr(e, 'message') else e))

    return redirect('event-detail', pk=ticket_type.event.pk)

@login_required
def payment_view(request, reservation_id):
    reservation = get_object_or_404(Reservation, pk=reservation_id, user=request.user)

    if reservation.payment_status == Reservation.PAID:
        messages.info(request, "Cette réservation est déjà payée.")
        return redirect('user-reservations')

    if request.method == 'POST':
        method = request.POST.get('method')
        phone = request.POST.get('phone_number', '')
        try:
            payment = TicketService.process_payment(request.user, reservation.id, method, phone)
            messages.success(request, f"Paiement réussi ! Référence : {payment.reference}")
            return redirect('user-reservations')
        except ValidationError as e:
            messages.error(request, str(e.message if hasattr(e, 'message') else e))

    return render(request, 'tickets/payment.html', {
        'reservation': reservation,
        'methods': Payment.METHOD_CHOICES,
    })

@login_required
def cancel_reservation_view(request, reservation_id):
    reservation = get_object_or_404(Reservation, pk=reservation_id)
    if request.method == 'POST':
        try:
            TicketService.cancel_reservation(request.user, reservation.id)
            messages.success(request, "Réservation annulée.")
        except ValidationError as e:
            messages.error(request, str(e.message if hasattr(e, 'message') else e))
            
    next_url = request.POST.get('next', 'user-reservations')
    return redirect(next_url)

@login_required
def organizer_dashboard(request):
    if not request.user.is_organizer_user() and not request.user.is_admin_user():
        messages.error(request, "Accès restreint aux organisateurs.")
        return redirect('event-list')
        
    events = Event.objects.filter(organizer=request.user)

    events_stats = []
    global_revenue = 0
    global_sold = 0
    global_confirmed = 0
    global_pending = 0

    for event in events:
        ticket_types = event.ticket_types.all()
        total_sold = sum(tt.sold_count for tt in ticket_types)
        revenue = sum(tt.sold_count * tt.price for tt in ticket_types)

        reservations = Reservation.objects.filter(
            ticket_type__event=event
        ).select_related('user', 'ticket_type').order_by('-created_at')

        confirmed = reservations.filter(status=Reservation.CONFIRMED)
        pending_count = confirmed.filter(payment_status=Reservation.PENDING).count()

        events_stats.append({
            'event': event,
            'ticket_types': ticket_types,
            'total_sold': total_sold,
            'revenue': revenue,
            'reservations': reservations,
            'confirmed_count': confirmed.count(),
            'pending_count': pending_count,
        })

        global_revenue += revenue
        global_sold += total_sold
        global_confirmed += confirmed.count()
        global_pending += pending_count

    summary = {
        'total_events': events.count(),
        'global_revenue': global_revenue,
        'global_sold': global_sold,
        'global_confirmed': global_confirmed,
        'global_pending': global_pending,
    }

    return render(request, 'tickets/organizer_dashboard.html', {
        'events_stats': events_stats,
        'summary': summary,
    })
