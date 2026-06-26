from django.contrib import admin

from .models import PaguelofacilTransaction, Payout


@admin.register(PaguelofacilTransaction)
class PaguelofacilTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'internal_reference', 'booking', 'client', 'amount',
        'status', 'paguelofacil_id', 'created_at', 'approved_at',
    )
    list_filter = ('status', 'payment_type', 'created_at')
    search_fields = ('internal_reference', 'paguelofacil_id', 'client__email')
    readonly_fields = (
        'internal_reference', 'paguelofacil_id', 'paguelofacil_auth_code',
        'request_payload', 'response_payload', 'webhook_payloads',
        'created_at', 'updated_at', 'approved_at',
    )
    date_hierarchy = 'created_at'


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = (
        'recipient', 'recipient_kind', 'amount', 'status',
        'method', 'reference', 'paid_at',
    )
    list_filter = ('status', 'recipient_kind', 'method')
    search_fields = ('recipient__email', 'reference', 'booking__booking_code')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
