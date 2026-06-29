from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_superuser')
    list_filter = ('role', 'is_staff', 'is_superuser')
    # On expose le champ "role" dans le formulaire d'edition et de creation.
    fieldsets = UserAdmin.fieldsets + (
        ("Rôle EVENTPRO", {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Rôle EVENTPRO", {'fields': ('role',)}),
    )
