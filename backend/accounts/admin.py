from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    # Forms de Unfold para que el cambio de contraseña / alta usen el estilo del tema.
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    list_display = [
        'username', 'email', 'first_name', 'last_name',
        'role', 'is_verified', 'is_active', 'created_at'
    ]
    list_filter = ['role', 'is_verified', 'is_active', 'country']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    list_editable = ['role', 'is_verified']
    actions = ['mark_verified', 'mark_unverified']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Pulsar', {
            'fields': ('role', 'avatar', 'phone', 'city', 'country', 'bio', 'is_verified')
        }),
    )

    @admin.action(description='Marcar como verificado')
    def mark_verified(self, request, queryset):
        n = queryset.update(is_verified=True)
        self.message_user(request, f'{n} usuario(s) marcados como verificados.')

    @admin.action(description='Quitar verificación')
    def mark_unverified(self, request, queryset):
        n = queryset.update(is_verified=False)
        self.message_user(request, f'{n} usuario(s) sin verificación.')
