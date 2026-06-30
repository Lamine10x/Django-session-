from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def notifications_list(request):
    notifs = request.user.notifications.all()
    # Marque tout comme lu a l'ouverture de la page
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'notifications/notifications_list.html', {'notifications': notifs})

@login_required
def notification_open(request, pk):
    notif = request.user.notifications.filter(pk=pk).first()
    if notif:
        notif.is_read = True
        notif.save()
        if notif.url:
            return redirect(notif.url)
    return redirect('notifications-list')
