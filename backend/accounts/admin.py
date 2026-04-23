from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        'username', 'email', 'first_name', 'last_name',
        'role', 'is_verified', 'is_active', 'created_at'
    ]
    list_filter = ['role', 'is_verified', 'is_active', 'country']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    list_editable = ['role', 'is_verified']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Pulsar', {
            'fields': ('role', 'avatar', 'phone', 'city', 'country', 'bio', 'is_verified')
        }),
    )
