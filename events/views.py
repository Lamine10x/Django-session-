from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Q
from .models import Event
from .services import EventService

def event_list(request):
    if request.user.is_authenticated and (request.user.is_organizer_user() or request.user.is_admin_user()):
        events = Event.objects.filter(Q(status=Event.PUBLISHED) | Q(organizer=request.user))
    else:
        events = Event.objects.filter(status=Event.PUBLISHED)

    # Filtre par categorie (apprecie par le participant)
    selected_category = request.GET.get('category')
    valid_categories = [choice[0] for choice in Event.CATEGORY_CHOICES]
    if selected_category in valid_categories:
        events = events.filter(category=selected_category)
    else:
        selected_category = None

    return render(request, 'events/event_list.html', {
        'events': events,
        'categories': Event.CATEGORY_CHOICES,
        'selected_category': selected_category,
    })

def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if event.status == Event.DRAFT:
        if not request.user.is_authenticated or (request.user != event.organizer and not request.user.is_admin_user()):
            messages.error(request, "Vous n'avez pas l'autorisation d'accéder à ce brouillon.")
            return redirect('event-list')
            
    ticket_types = event.ticket_types.all() if hasattr(event, 'ticket_types') else []
    return render(request, 'events/event_detail.html', {
        'event': event,
        'ticket_types': ticket_types
    })

@login_required
def event_create(request):
    if not request.user.is_organizer_user() and not request.user.is_admin_user():
        messages.error(request, "Seuls les organisateurs peuvent créer des événements.")
        return redirect('event-list')
        
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        date = request.POST.get('date')
        end_date = request.POST.get('end_date')
        location = request.POST.get('location')
        max_capacity = request.POST.get('max_capacity')
        status_val = request.POST.get('status', Event.DRAFT)
        category = request.POST.get('category', Event.CONCERT)

        try:
            event = EventService.create_event(
                title=title,
                description=description,
                date=date,
                end_date=end_date,
                location=location,
                max_capacity=max_capacity,
                organizer=request.user,
                status=status_val,
                category=category
            )
            messages.success(request, "Événement créé avec succès !")
            return redirect('event-detail', pk=event.pk)
        except ValidationError as e:
            messages.error(request, str(e.message if hasattr(e, 'message') else e))

    return render(request, 'events/event_form.html', {
        'statuses': Event.STATUS_CHOICES,
        'categories': Event.CATEGORY_CHOICES,
    })

@login_required
def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.user != event.organizer and not request.user.is_admin_user():
        messages.error(request, "Vous n'êtes pas l'organisateur de cet événement.")
        return redirect('event-detail', pk=event.pk)
        
    if request.method == 'POST':
        event.title = request.POST.get('title')
        event.description = request.POST.get('description')
        event.date = request.POST.get('date')
        event.end_date = request.POST.get('end_date') or None
        event.location = request.POST.get('location')
        event.max_capacity = request.POST.get('max_capacity')

        category = request.POST.get('category')
        if category in [choice[0] for choice in Event.CATEGORY_CHOICES]:
            event.category = category

        new_status = request.POST.get('status')
        try:
            EventService._validate_dates(event.date, event.end_date)
            if new_status and new_status != event.status:
                EventService.update_event_status(event, new_status)
            event.save()
            messages.success(request, "Événement mis à jour avec succès !")
            return redirect('event-detail', pk=event.pk)
        except ValidationError as e:
            messages.error(request, str(e.message if hasattr(e, 'message') else e))
            
    return render(request, 'events/event_form.html', {
        'event': event,
        'statuses': Event.STATUS_CHOICES,
        'categories': Event.CATEGORY_CHOICES,
    })

@login_required
def event_status_change(request, pk, new_status):
    event = get_object_or_404(Event, pk=pk)
    if request.user != event.organizer and not request.user.is_admin_user():
        messages.error(request, "Vous n'y êtes pas autorisé.")
        return redirect('event-detail', pk=event.pk)
        
    try:
        EventService.update_event_status(event, new_status)
        messages.success(request, f"Statut mis à jour : {event.get_status_display()}")
    except ValidationError as e:
        messages.error(request, str(e.message if hasattr(e, 'message') else e))
        
    return redirect('event-detail', pk=event.pk)
