from django.contrib import admin
from .models import Booking, Payment, Message, Notification, Review, PlatformConfig


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ['commission_showroots', 'commission_partner', 'talent_payout', 'created_at']


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ['sender', 'content', 'created_at']
    can_delete = False


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
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
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'booking', 'client', 'amount', 'payment_type',
        'payment_status', 'commission_showroots', 'commission_partner',
        'talent_payout', 'created_at'
    ]
    list_filter = ['payment_status', 'payment_type', 'payment_method']
    search_fields = ['booking__id', 'client__first_name', 'transaction_ref']
    readonly_fields = ['commission_showroots', 'commission_partner', 'talent_payout']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'sender', 'content_preview', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['content', 'sender__first_name']

    def content_preview(self, obj):
        return obj.content[:60] + '...' if len(obj.content) > 60 else obj.content
    content_preview.short_description = 'Mensaje'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read']
    search_fields = ['user__first_name', 'title', 'message']
    list_editable = ['is_read']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'talent', 'rating', 'comment_preview', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['client__first_name', 'talent__stage_name', 'comment']

    def comment_preview(self, obj):
        return obj.comment[:60] + '...' if len(obj.comment) > 60 else obj.comment
    comment_preview.short_description = 'Comentario'


@admin.register(PlatformConfig)
class PlatformConfigAdmin(admin.ModelAdmin):
    list_display = [
        'standard_commission_rate', 'premium_commission_rate',
        'partner_commission_rate', 'service_fee_name', 'updated_at'
    ]
    fieldsets = (
        ('Comisiones por Nivel', {
            'fields': ('standard_commission_rate', 'premium_commission_rate', 'partner_commission_rate'),
            'description': 'Standard: 20% | Premium: 15% | Partner: 30% de la comisión de la plataforma'
        }),
        ('Fee al Cliente ("Gestión y garantía")', {
            'fields': (
                'service_fee_name', 'service_fee_mode', 'service_fee_rate',
                'service_fee_small', 'service_fee_medium', 'service_fee_large'
            ),
            'description': 'Fee cobrado al cliente por gestión del evento'
        }),
    )

    def has_add_permission(self, request):
        # Only allow one config instance
        return not PlatformConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
