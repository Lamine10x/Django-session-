def navbar_badges(request):
    """Expose les compteurs cloche/coeur a toutes les pages."""
    if not request.user.is_authenticated:
        return {}
    return {
        'unread_notifications_count': request.user.notifications.filter(is_read=False).count(),
        'recent_notifications': request.user.notifications.all()[:6],
        'favorites_count': request.user.favorite_events.count(),
    }
