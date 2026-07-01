from django.contrib import admin
from .models import TicketType, Reservation, Payment

@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'price', 'quota', 'sold_count')
    list_filter = ('event',)

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('ticket_code', 'user', 'ticket_type', 'status', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status')
    search_fields = ('ticket_code', 'user__username')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('reference', 'reservation', 'method', 'amount', 'is_successful', 'created_at')
    list_filter = ('method', 'is_successful')
    search_fields = ('reference',)
