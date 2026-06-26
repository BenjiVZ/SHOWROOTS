from rest_framework import serializers

from .models import PaguelofacilTransaction, Payout


class CreateCheckoutSerializer(serializers.Serializer):
    """Input para POST /api/payments/paguelofacil/checkout/"""
    booking_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=1)
    payment_type = serializers.ChoiceField(
        choices=PaguelofacilTransaction.PAYMENT_TYPE_CHOICES,
        default='full',
    )


class PaguelofacilTransactionSerializer(serializers.ModelSerializer):
    booking_code = serializers.CharField(source='booking.booking_code', read_only=True)
    client_email = serializers.CharField(source='client.email', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = PaguelofacilTransaction
        fields = [
            'id', 'booking', 'booking_code', 'client_email',
            'amount', 'currency', 'payment_type', 'description',
            'status', 'status_display',
            'internal_reference', 'paguelofacil_id', 'paguelofacil_auth_code',
            'created_at', 'updated_at', 'approved_at',
        ]
        read_only_fields = fields


class PayoutSerializer(serializers.ModelSerializer):
    recipient_email = serializers.CharField(source='recipient.email', read_only=True)
    recipient_name = serializers.SerializerMethodField()
    booking_code = serializers.CharField(source='booking.booking_code', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Payout
        fields = [
            'id', 'booking', 'booking_code',
            'recipient', 'recipient_email', 'recipient_name', 'recipient_kind',
            'amount', 'currency',
            'status', 'status_display', 'method', 'reference', 'notes',
            'created_at', 'paid_at',
        ]
        read_only_fields = ['id', 'created_at']

    def get_recipient_name(self, obj):
        u = obj.recipient
        return f"{u.first_name} {u.last_name}".strip() or u.email
