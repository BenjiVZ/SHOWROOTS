from rest_framework import serializers
from accounts.serializers import UserSerializer
from talents.serializers import TalentListSerializer
from .models import Booking, Payment, Message, Notification, Review, PlatformConfig


class ReviewSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    client_avatar = serializers.ImageField(source='client.avatar', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'booking', 'client', 'client_name', 'client_avatar',
            'talent', 'rating', 'comment', 'created_at'
        ]
        read_only_fields = ['id', 'client', 'talent', 'created_at']


class PaymentSerializer(serializers.ModelSerializer):
    payment_status_display = serializers.CharField(
        source='get_payment_status_display', read_only=True
    )

    class Meta:
        model = Payment
        fields = [
            'id', 'booking', 'client', 'amount', 'payment_type',
            'payment_status', 'payment_status_display', 'payment_method',
            'commission_showroots', 'commission_partner', 'talent_payout',
            'transaction_ref', 'notes', 'created_at'
        ]
        read_only_fields = [
            'id', 'client', 'commission_showroots', 'commission_partner',
            'talent_payout', 'created_at'
        ]


class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['booking', 'amount', 'payment_type', 'payment_method', 'notes']

    def validate_booking(self, value):
        # Payment only allowed on accepted bookings
        if value.status not in ('aceptada', 'pendiente_pago'):
            raise serializers.ValidationError(
                'Solo se puede pagar una reserva aceptada o pendiente de pago.'
            )
        return value

    def create(self, validated_data):
        validated_data['client'] = self.context['request'].user
        validated_data['payment_status'] = 'completed'  # Simulated for now
        payment = Payment(**validated_data)
        payment.calculate_commissions()
        payment.save()
        return payment


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    sender_avatar = serializers.ImageField(source='sender.avatar', read_only=True)

    class Meta:
        model = Message
        fields = [
            'id', 'booking', 'sender', 'sender_name', 'sender_avatar',
            'content', 'file_url', 'is_read', 'created_at'
        ]
        read_only_fields = ['id', 'sender', 'created_at']


class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['booking', 'content', 'file_url']

    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


class NotificationSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(
        source='get_notification_type_display', read_only=True
    )

    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'notification_type', 'type_display',
            'title', 'message', 'link', 'is_read', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class BookingListSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    talent_name = serializers.CharField(source='talent.stage_name', read_only=True)
    talent_avatar = serializers.ImageField(source='talent.cover_photo', read_only=True)
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    has_review = serializers.SerializerMethodField()
    remaining_balance = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    total_client_cost = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Booking
        fields = [
            'id', 'client_name', 'talent_name', 'talent_avatar',
            'event_type', 'event_type_display', 'event_name',
            'event_date', 'event_time_start', 'event_time_end',
            'event_location', 'event_city', 'guest_count',
            'budget', 'precio_estimado', 'quoted_price', 'amount_paid',
            'service_fee', 'total_client_cost', 'remaining_balance',
            'booking_type', 'description',
            'additional_services', 'expires_at',
            'status', 'status_display',
            'has_review', 'created_at'
        ]

    def get_has_review(self, obj):
        return hasattr(obj, 'review')


class BookingDetailSerializer(serializers.ModelSerializer):
    client = UserSerializer(read_only=True)
    talent = TalentListSerializer(read_only=True)
    review = ReviewSerializer(read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    remaining_balance = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    total_client_cost = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    service_fee_name = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id', 'client', 'talent', 'partner', 'booking_type',
            'event_type', 'event_type_display',
            'event_name', 'event_date', 'event_time_start', 'event_time_end',
            'event_duration_hours', 'event_location', 'event_city',
            'event_indoor', 'guest_count', 'description', 'genre_preference',
            'client_final_name', 'client_final_email', 'client_final_phone',
            'budget', 'precio_estimado', 'quoted_price',
            'deposit_percentage', 'amount_paid',
            'service_fee', 'service_fee_name', 'total_client_cost', 'remaining_balance',
            'additional_services', 'additional_services_notes', 'expires_at',
            'status', 'status_display',
            'talent_notes', 'client_notes',
            'review', 'payments', 'messages',
            'created_at', 'updated_at'
        ]

    def get_service_fee_name(self, obj):
        config = PlatformConfig.get_config()
        return config.service_fee_name


class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            'talent', 'event_type', 'event_name', 'event_date',
            'event_time_start', 'event_time_end', 'event_duration_hours',
            'event_location', 'event_city', 'event_indoor',
            'guest_count', 'description', 'genre_preference',
            'budget', 'client_notes',
            # Additional services
            'additional_services', 'additional_services_notes',
            # Partner fields
            'client_final_name', 'client_final_email', 'client_final_phone',
        ]

    def validate_talent(self, value):
        if not value.is_approved:
            raise serializers.ValidationError('Este talento aun no ha sido aprobado.')
        if not value.is_available:
            raise serializers.ValidationError('Este talento no esta disponible.')
        return value

    def validate(self, data):
        # Check availability
        from talents.models import Availability
        talent = data['talent']
        event_date = data['event_date']
        blocked = Availability.objects.filter(
            talent=talent, date=event_date, status__in=['blocked', 'booked']
        ).exists()
        if blocked:
            raise serializers.ValidationError(
                {'event_date': 'El talento no esta disponible en esta fecha.'}
            )
        # Check no existing confirmed booking on same date
        existing = Booking.objects.filter(
            talent=talent, event_date=event_date,
            status__in=['aceptada', 'pendiente_pago', 'confirmada']
        ).exists()
        if existing:
            raise serializers.ValidationError(
                {'event_date': 'El talento ya tiene una reserva confirmada en esta fecha.'}
            )
        return data

    def create(self, validated_data):
        from django.utils import timezone
        from datetime import timedelta
        user = self.context['request'].user
        validated_data['client'] = user
        # If user is a Partner, mark booking accordingly
        if user.role == 'partner':
            validated_data['partner'] = user
            validated_data['booking_type'] = 'partner'
        # Set auto-expiration (48 hours)
        validated_data['expires_at'] = timezone.now() + timedelta(hours=48)
        booking = Booking(**validated_data)
        # Auto-calculate estimated price
        booking.calculate_estimated_price()
        # Auto-calculate service fee ("Gestión y garantía")
        booking.calculate_service_fee()
        booking.save()
        return booking


class PartnerStatsSerializer(serializers.Serializer):
    """Aggregated stats for the Partner dashboard."""
    total_bookings = serializers.IntegerField()
    active_bookings = serializers.IntegerField()
    completed_bookings = serializers.IntegerField()
    total_commission_earned = serializers.DecimalField(max_digits=12, decimal_places=2)
    pending_commission = serializers.DecimalField(max_digits=12, decimal_places=2)


class PlatformConfigSerializer(serializers.ModelSerializer):
    """Serializer for admin-configurable platform settings."""
    standard_commission_pct = serializers.SerializerMethodField()
    premium_commission_pct = serializers.SerializerMethodField()
    partner_commission_pct = serializers.SerializerMethodField()
    service_fee_pct = serializers.SerializerMethodField()

    class Meta:
        model = PlatformConfig
        fields = [
            'standard_commission_rate', 'premium_commission_rate',
            'partner_commission_rate',
            'standard_commission_pct', 'premium_commission_pct',
            'partner_commission_pct',
            'service_fee_name', 'service_fee_mode', 'service_fee_rate',
            'service_fee_pct',
            'service_fee_small', 'service_fee_medium', 'service_fee_large',
            'updated_at'
        ]
        read_only_fields = ['updated_at']

    def get_standard_commission_pct(self, obj):
        return float(obj.standard_commission_rate * 100)

    def get_premium_commission_pct(self, obj):
        return float(obj.premium_commission_rate * 100)

    def get_partner_commission_pct(self, obj):
        return float(obj.partner_commission_rate * 100)

    def get_service_fee_pct(self, obj):
        return float(obj.service_fee_rate * 100)

