from django.contrib import admin
from django.utils.html import format_html

from unfold.admin import ModelAdmin, TabularInline

from .models import (
    Booking, Payment, Message, Notification, Review, PlatformConfig,
    PartnerProductionProfile, ProductionPack, OpenGigRequest,
    PaymentMethod, ManualPaymentOrder,
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


# ── Sistema de pagos (métodos + revisión manual) ──

@admin.register(PaymentMethod)
class PaymentMethodAdmin(ModelAdmin):
    list_display = ['name', 'kind', 'is_active', 'display_order', 'payment_method_code', 'requires_proof']
    list_filter = ['kind', 'is_active']
    list_editable = ['is_active', 'display_order']
    search_fields = ['name', 'slug', 'account_holder', 'bank_name']
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Identidad', {
            'fields': ('name', 'slug', 'kind', 'provider', 'is_active', 'display_order', 'logo')
        }),
        ('Cómo paga el cliente (manual)', {
            'fields': (
                'instructions', 'account_holder', 'bank_name',
                'account_number', 'account_type', 'phone', 'extra_info',
                'requires_proof', 'payment_method_code',
            ),
            'description': 'Estos datos se le muestran al cliente en el checkout cuando elige este método.'
        }),
    )


@admin.register(ManualPaymentOrder)
class ManualPaymentOrderAdmin(ModelAdmin):
    list_display = [
        'id', 'booking', 'client', 'method', 'amount',
        'reference', 'receipt_thumb', 'status', 'created_at',
    ]
    list_filter = ['status', 'method', 'created_at']
    search_fields = ['id', 'booking__id', 'client__email', 'client__first_name', 'reference']
    date_hierarchy = 'created_at'
    actions = ['approve_orders', 'reject_orders']
    readonly_fields = [
        'booking', 'client', 'method', 'amount', 'payment_type', 'reference',
        'client_note', 'receipt_preview', 'status', 'payment',
        'reviewed_by', 'reviewed_at', 'created_at', 'updated_at',
    ]
    fieldsets = (
        ('Pago declarado por el cliente', {
            'fields': ('booking', 'client', 'method', 'amount', 'payment_type', 'reference', 'client_note')
        }),
        ('Comprobante', {'fields': ('receipt_preview',)}),
        ('Revisión', {
            'fields': ('status', 'rejection_reason', 'review_notes', 'payment', 'reviewed_by', 'reviewed_at'),
            'description': 'Usá las acciones "Aprobar" / "Rechazar" de la lista. Para rechazar con un motivo, escribilo en "rejection_reason", guardá, y luego corré la acción Rechazar.'
        }),
    )

    def has_add_permission(self, request):
        # Las órdenes las crea el cliente desde el checkout, no a mano.
        return False

    def receipt_thumb(self, obj):
        if obj.receipt:
            return format_html('<img src="{}" style="height:34px;border-radius:4px" />', obj.receipt.url)
        return '—'
    receipt_thumb.short_description = 'Comprobante'

    def receipt_preview(self, obj):
        if obj.receipt:
            return format_html(
                '<a href="{}" target="_blank" rel="noopener">'
                '<img src="{}" style="max-height:260px;border-radius:10px;border:1px solid #ddd" /></a>',
                obj.receipt.url, obj.receipt.url,
            )
        return '— sin comprobante —'
    receipt_preview.short_description = 'Comprobante'

    @admin.action(description='✓ Aprobar pago (confirma reserva + genera payouts)')
    def approve_orders(self, request, queryset):
        from .payment_notifications import notify_client_manual_payment_approved
        done = 0
        for order in queryset:
            if order.status == 'approved':
                continue
            order.approve(by_user=request.user)
            try:
                notify_client_manual_payment_approved(order)
            except Exception:
                pass
            done += 1
        self.message_user(request, f'{done} pago(s) aprobados y reserva(s) confirmadas.')

    @admin.action(description='✗ Rechazar pago (avisa al cliente)')
    def reject_orders(self, request, queryset):
        from .payment_notifications import notify_client_manual_payment_rejected
        done = 0
        for order in queryset:
            if order.status == 'approved':
                continue
            reason = order.rejection_reason or 'No pudimos validar el comprobante. Verificá los datos y reintentá.'
            order.reject(by_user=request.user, reason=reason)
            try:
                notify_client_manual_payment_rejected(order)
            except Exception:
                pass
            done += 1
        self.message_user(request, f'{done} pago(s) rechazados.')
