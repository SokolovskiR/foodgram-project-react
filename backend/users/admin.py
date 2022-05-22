from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """User administration."""
    list_display = (
        'pk',
        'username',
        'first_name',
        'last_name',
        'email',
        'is_active',
        'is_superuser',
        'last_login'
    )
    list_editable = ('is_active', 'is_superuser')
    list_filter = ('is_active', 'is_superuser')
    search_fields = ('username','email', 'last_name')
