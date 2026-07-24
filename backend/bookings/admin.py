from django.contrib import admin

from unfold.admin import ModelAdmin, TabularInline

from .models import (
    Booking, Payment, Message, Notification, Review, PlatformConfig,
    PartnerProductionProfile, ProductionPack, OpenGigRequest,
)


class PaymentInline(TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ['commission_showroots', 'commission_partner', 'talent_payout', 'created_at']


class MessageInline(TabularInline):
    model = Message
    extra = 0
    readonly_fields = ['sender', 'content', 'created_at']
    can_delete = False


@admin.register(Booking)
class BookingAdmin(ModelAdmin):
    list_display = [
        'id', 'client', 'talent', 'event_type', 'event_date',
        'precio_estimado', 'quoted_price', 'amount_paid',
        'status', 'booking_type', 'created_at'
    ]
    list_filter = ['status', 'event_type', 'booking_type', 'event_date']
    search_fields = [
        'client__first_name', 'client__last_name',
        'talent__stage_name', 'event_name', 'event_location'
    ]
    list_editable = ['status']
    inlines = [PaymentInline, MessageInline]
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Relaciones', {
            'fields': ('client', 'talent', 'partner', 'booking_type')
        }),
        ('Evento', {
            'fields': (
                'event_type', 'event_name', 'event_date',
                'event_time_start', 'event_time_end', 'event_duration_hours',
                'event_location', 'event_city', 'guest_count', 'description'
            )
        }),
        ('Precios', {
            'fields': (
                'budget', 'precio_estimado', 'quoted_price',
                'deposit_percentage', 'amount_paid', 'service_fee'
            )
        }),
        ('Estado', {
            'fields': ('status', 'talent_notes', 'client_notes', 'created_at', 'updated_at')
        }),
    )


@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = [
        'id', 'booking', 'client', 'amount', 'payment_type',
        'payment_status', 'commission_showroots', 'commission_partner',
        'talent_payout', 'created_at'
    ]
    list_filter = ['payment_status', 'payment_type', 'payment_method']
    search_fields = ['booking__id', 'client__first_name', 'transaction_ref']
    readonly_fields = ['commission_showroots', 'commission_partner', 'talent_payout']


@admin.register(Message)
class MessageAdmin(ModelAdmin):
    list_display = ['id', 'booking', 'sender', 'content_preview', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['content', 'sender__first_name']

    def content_preview(self, obj):
        return obj.content[:60] + '...' if len(obj.content) > 60 else obj.content
    content_preview.short_description = 'Mensaje'


@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display = ['id', 'user', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read']
    search_fields = ['user__first_name', 'title', 'message']
    list_editable = ['is_read']


@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    list_display = ['id', 'client', 'talent', 'rating', 'comment_preview', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['client__first_name', 'talent__stage_name', 'comment']

    def comment_preview(self, obj):
        return obj.comment[:60] + '...' if len(obj.comment) > 60 else obj.comment
    comment_preview.short_description = 'Comentario'


@admin.register(PlatformConfig)
class PlatformConfigAdmin(ModelAdmin):
    list_display = [
        'standard_commission_rate', 'premium_commission_rate',
        'partner_commission_rate', 'service_fee_name', 'updated_at'
    ]
    fieldsets = (
        ('Comisiones por plan', {
            'fields': ('standard_commission_rate', 'pro_commission_rate', 'premium_commission_rate', 'partner_commission_rate'),
            'description': 'Standard: 20% | Pro: 15% | Premium: 12% | Aliado: 30% de la comisión de la plataforma'
        }),
        ('Fee al cliente ("Gestión y garantía")', {
            'fields': (
                'service_fee_name', 'service_fee_mode', 'service_fee_rate',
                'service_fee_small', 'service_fee_medium', 'service_fee_large'
            ),
            'description': 'Fee cobrado al cliente por gestión del evento'
        }),
    )

    def has_add_permission(self, request):
        return not PlatformConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


# ── Marketplace de producción (Aliados) ──

@admin.register(PartnerProductionProfile)
class PartnerProductionProfileAdmin(ModelAdmin):
    list_display = ['user', 'main_city', 'status', 'coverage_radius_km', 'onboarding_step']
    list_filter = ['status', 'main_city']
    search_fields = ['user__email', 'user__first_name', 'main_city']
    actions = ['verify_partners', 'reject_partners']

    @admin.action(description='Verificar aliados seleccionados')
    def verify_partners(self, request, queryset):
        n = queryset.update(status='verified')
        self.message_user(request, f'{n} aliado(s) verificados.')

    @admin.action(description='Rechazar aliados')
    def reject_partners(self, request, queryset):
        n = queryset.update(status='rejected')
        self.message_user(request, f'{n} aliado(s) rechazados.')


@admin.register(ProductionPack)
class ProductionPackAdmin(ModelAdmin):
    list_display = ['name', 'partner', 'category', 'event_size', 'price', 'status', 'rentals_count']
    list_filter = ['category', 'event_size', 'status']
    search_fields = ['name', 'partner__user__email']
    actions = ['publish_packs', 'pause_packs']

    @admin.action(description='Publicar packs')
    def publish_packs(self, request, queryset):
        n = queryset.update(status='published')
        self.message_user(request, f'{n} pack(s) publicados.')

    @admin.action(description='Pausar packs')
    def pause_packs(self, request, queryset):
        n = queryset.update(status='paused')
        self.message_user(request, f'{n} pack(s) pausados.')


@admin.register(OpenGigRequest)
class OpenGigRequestAdmin(ModelAdmin):
    list_display = ['id', 'client', 'event_date', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['client__email', 'client__first_name']
    date_hierarchy = 'event_date'
