from django.utils import timezone
from django.contrib import admin

from unfold.admin import ModelAdmin

from .models import PaguelofacilTransaction, Payout


@admin.register(PaguelofacilTransaction)
class PaguelofacilTransactionAdmin(ModelAdmin):
    list_display = (
        'internal_reference', 'booking', 'client', 'amount',
        'status', 'refunded_amount', 'paguelofacil_id', 'created_at', 'approved_at',
    )
    list_filter = ('status', 'payment_type', 'created_at')
    search_fields = ('internal_reference', 'paguelofacil_id', 'client__email')
    readonly_fields = (
        'internal_reference', 'paguelofacil_id', 'paguelofacil_auth_code',
        'refunded_amount', 'request_payload', 'response_payload', 'webhook_payloads',
        'created_at', 'updated_at', 'approved_at',
    )
    date_hierarchy = 'created_at'


@admin.register(Payout)
class PayoutAdmin(ModelAdmin):
    list_display = (
        'recipient', 'recipient_kind', 'amount', 'status',
        'method', 'reference', 'paid_at',
    )
    list_filter = ('status', 'recipient_kind', 'method')
    search_fields = ('recipient__email', 'reference', 'booking__booking_code')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    actions = ['mark_paid']

    @admin.action(description='Marcar como PAGADO')
    def mark_paid(self, request, queryset):
        n = 0
        for payout in queryset.exclude(status='paid'):
            payout.status = 'paid'
            payout.paid_at = timezone.now()
            payout.created_by = request.user
            payout.save(update_fields=['status', 'paid_at', 'created_by'])
            n += 1
        self.message_user(request, f'{n} payout(s) marcados como pagados.')
