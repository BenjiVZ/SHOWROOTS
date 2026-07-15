from rest_framework import serializers
from accounts.serializers import UserSerializer
from talents.serializers import TalentListSerializer
from .models import (
    Booking, Payment, Message, Notification, Review, PlatformConfig,
    PremiumInvitation, ClientCredit,
    PartnerProductionProfile, PartnerProductionPhoto,
    ProductionPack, BookingPack, PackBundle,
    OpenGigRequest, GigOffer,
)


class ReviewSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    client_avatar = serializers.ImageField(source='client.avatar', read_only=True)
    event_type_display = serializers.CharField(source='booking.get_event_type_display', read_only=True)
    event_guest_count = serializers.IntegerField(source='booking.guest_count', read_only=True)
    event_date = serializers.DateField(source='booking.event_date', read_only=True)
    is_verified = serializers.SerializerMethodField()

    def get_is_verified(self, obj):
        # Una reseña existe sólo si el booking fue completado → siempre verificada
        return obj.booking.status == 'completada'

    class Meta:
        model = Review
        fields = [
            'id', 'booking', 'client', 'client_name', 'client_avatar',
            'talent', 'rating',
            'rating_punctuality', 'rating_music_selection',
            'rating_crowd_reading', 'rating_technique', 'rating_communication',
            'comment', 'response', 'response_at', 'created_at',
            'event_type_display', 'event_guest_count', 'event_date', 'is_verified',
        ]
        read_only_fields = ['id', 'client', 'talent', 'response_at', 'created_at']


class PremiumInvitationSerializer(serializers.ModelSerializer):
    talent_name = serializers.CharField(source='talent.stage_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = PremiumInvitation
        fields = [
            'id', 'talent', 'talent_name', 'invited_by', 'status', 'status_display',
            'message', 'sent_at', 'expires_at', 'responded_at',
        ]
        read_only_fields = ['id', 'invited_by', 'sent_at', 'responded_at']


class FlaggedMessageSerializer(serializers.ModelSerializer):
    """Para admin: ver mensajes que el scanner anti-disinter capturó."""
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    booking_code = serializers.CharField(source='booking.booking_code', read_only=True)

    class Meta:
        model = Message
        fields = [
            'id', 'booking', 'booking_code', 'sender', 'sender_name',
            'content', 'raw_content', 'flagged', 'flagged_categories',
            'created_at',
        ]


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
    talent_name = serializers.SerializerMethodField()
    talent_avatar = serializers.SerializerMethodField()
    is_service_only = serializers.BooleanField(read_only=True)
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
            'id', 'booking_code', 'client_name', 'talent_name', 'talent_avatar',
            'is_service_only',
            'event_type', 'event_type_display', 'event_name',
            'event_date', 'event_time_start', 'event_time_end',
            'event_location', 'event_city', 'guest_count',
            'budget', 'precio_estimado', 'quoted_price', 'amount_paid',
            'service_fee', 'tax_amount', 'total_client_cost', 'remaining_balance',
            'booking_type', 'description',
            'additional_services', 'expires_at',
            'status', 'status_display',
            'has_review', 'created_at'
        ]

    def get_has_review(self, obj):
        return hasattr(obj, 'review')

    def get_talent_name(self, obj):
        return obj.talent.stage_name if obj.talent else None

    def get_talent_avatar(self, obj):
        if obj.talent and obj.talent.cover_photo:
            try:
                return obj.talent.cover_photo.url
            except Exception:
                return None
        return None


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
    packs_subtotal = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    total_to_pay = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    is_service_only = serializers.BooleanField(read_only=True)
    service_fee_name = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id', 'booking_code', 'client', 'talent', 'is_service_only', 'partner', 'booking_type',
            'event_type', 'event_type_display',
            'event_name', 'event_date', 'event_time_start', 'event_time_end',
            'event_duration_hours', 'event_location', 'event_city',
            'event_indoor', 'guest_count', 'description', 'genre_preference',
            'client_final_name', 'client_final_email', 'client_final_phone',
            'budget', 'precio_estimado', 'quoted_price',
            'deposit_percentage', 'amount_paid',
            'service_fee', 'service_fee_name', 'tax_amount',
            'packs_subtotal', 'total_to_pay',
            'total_client_cost', 'remaining_balance',
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
            # Devueltos en la respuesta (read-only) para poder encadenar acciones
            # tras crear la reserva (agregar packs de producción, mostrar código).
            'id', 'booking_code', 'status',
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
        read_only_fields = ['id', 'booking_code', 'status']

    def validate_talent(self, value):
        if not value.is_approved:
            raise serializers.ValidationError('Este talento aun no ha sido aprobado.')
        if not value.is_available:
            raise serializers.ValidationError('Este talento no esta disponible.')
        return value

    def validate(self, data):
        # Reserva de solo-servicios (sin DJ): no hay talento que validar.
        talent = data.get('talent')
        if talent is None:
            return data
        # Check availability
        from talents.models import Availability
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
    pack_commission_pct = serializers.SerializerMethodField()
    service_fee_pct = serializers.SerializerMethodField()

    class Meta:
        model = PlatformConfig
        fields = [
            'standard_commission_rate', 'premium_commission_rate',
            'partner_commission_rate', 'pack_commission_rate',
            'standard_commission_pct', 'premium_commission_pct',
            'partner_commission_pct', 'pack_commission_pct',
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

    def get_pack_commission_pct(self, obj):
        return float(obj.pack_commission_rate * 100)

    def get_service_fee_pct(self, obj):
        return float(obj.service_fee_rate * 100)


class PartnerProductionPhotoSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    class Meta:
        model = PartnerProductionPhoto
        fields = ['id', 'file', 'caption', 'order', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']

    def get_file(self, obj):
        """URL relativa (/media/...) — el frontend la resuelve vía proxy de Vite."""
        if not obj.file:
            return None
        try:
            return obj.file.url
        except Exception:
            return None


class PartnerProductionProfileSerializer(serializers.ModelSerializer):
    photos = PartnerProductionPhotoSerializer(many=True, read_only=True)
    photo_count = serializers.IntegerField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = PartnerProductionProfile
        fields = [
            'id', 'categories', 'main_city', 'coverage_radius_km',
            'travel_fee_extra', 'max_simultaneous_events', 'notes',
            'status', 'status_display', 'onboarding_step',
            'submitted_at', 'verified_at', 'rejection_reason',
            'photos', 'photo_count', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'status', 'status_display', 'submitted_at', 'verified_at',
            'rejection_reason', 'photos', 'photo_count', 'created_at', 'updated_at',
        ]

    def validate_categories(self, value):
        valid = {c[0] for c in PartnerProductionProfile.CATEGORY_CHOICES}
        invalid = [c for c in value if c not in valid]
        if invalid:
            raise serializers.ValidationError(f'Categorías inválidas: {invalid}')
        return value


class ProductionPackSerializer(serializers.ModelSerializer):
    """Pack para CRUD del partner (incluye campos write)."""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    event_size_display = serializers.CharField(source='get_event_size_display', read_only=True)

    class Meta:
        model = ProductionPack
        fields = [
            'id', 'name', 'category', 'category_display', 'short_description',
            'event_size', 'event_size_display', 'equipment_items',
            'price', 'currency',
            'includes_technician', 'includes_setup',
            'includes_dj', 'dj_name',
            'setup_hours_before',
            'available_days', 'cover_image',
            'status', 'rentals_count', 'rating_avg',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'rentals_count', 'rating_avg', 'created_at', 'updated_at']
        # cover_image queda como ImageField writable (default); el formateo lo hace to_representation

    def to_representation(self, instance):
        """En la salida, devolver cover_image como URL relativa (/media/...)."""
        data = super().to_representation(instance)
        if instance.cover_image:
            try:
                data['cover_image'] = instance.cover_image.url
            except Exception:
                data['cover_image'] = None
        else:
            data['cover_image'] = None
        return data


class ProductionPackPublicSerializer(serializers.ModelSerializer):
    """Pack para el catálogo público — incluye info del partner sin exponer todo."""
    cover_image = serializers.SerializerMethodField()
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    event_size_display = serializers.CharField(source='get_event_size_display', read_only=True)
    vendor = serializers.SerializerMethodField()

    class Meta:
        model = ProductionPack
        fields = [
            'id', 'name', 'category', 'category_display', 'short_description',
            'event_size', 'event_size_display', 'equipment_items',
            'price', 'currency',
            'includes_technician', 'includes_setup',
            'includes_dj', 'dj_name',
            'setup_hours_before',
            'cover_image', 'rentals_count', 'rating_avg', 'vendor',
        ]

    def get_cover_image(self, obj):
        """URL relativa (/media/...) — el frontend la resuelve vía proxy."""
        if not obj.cover_image:
            return None
        try:
            return obj.cover_image.url
        except Exception:
            return None

    def get_vendor(self, obj):
        u = obj.partner.user
        return {
            'id': u.id,
            'name': u.get_full_name() or u.username,
            'city': obj.partner.main_city,
            'is_dj_partner': u.role == 'talent',  # DJ que también es partner
        }


class BookingPackSerializer(serializers.ModelSerializer):
    pack = ProductionPackPublicSerializer(read_only=True)
    line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = BookingPack
        fields = ['id', 'pack', 'price_at_booking', 'quantity', 'notes', 'line_total', 'created_at']
        read_only_fields = ['id', 'price_at_booking', 'line_total', 'created_at']


class PackBundleSerializer(serializers.ModelSerializer):
    pack_ids = serializers.PrimaryKeyRelatedField(
        source='packs', queryset=ProductionPack.objects.all(),
        many=True, write_only=True, required=False
    )
    packs = ProductionPackPublicSerializer(many=True, read_only=True)
    base_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discounted_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = PackBundle
        fields = [
            'id', 'name', 'description', 'discount_percentage',
            'packs', 'pack_ids', 'status', 'rentals_count',
            'base_price', 'discounted_price',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'rentals_count', 'base_price', 'discounted_price', 'created_at', 'updated_at']


class PackBundlePublicSerializer(serializers.ModelSerializer):
    """Bundle para catálogo público."""
    packs = ProductionPackPublicSerializer(many=True, read_only=True)
    base_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discounted_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    vendor = serializers.SerializerMethodField()

    class Meta:
        model = PackBundle
        fields = [
            'id', 'name', 'description', 'discount_percentage',
            'packs', 'base_price', 'discounted_price', 'rentals_count', 'vendor',
        ]

    def get_vendor(self, obj):
        u = obj.partner.user
        return {
            'id': u.id,
            'name': u.get_full_name() or u.username,
            'city': obj.partner.main_city,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Solicitudes abiertas ("Uber para DJs")
# ─────────────────────────────────────────────────────────────────────────────

class GigOfferSerializer(serializers.ModelSerializer):
    # Datos del proveedor (DJ o partner)
    provider_name = serializers.SerializerMethodField()
    provider_avatar = serializers.SerializerMethodField()
    provider_city = serializers.SerializerMethodField()
    provider_user_id = serializers.SerializerMethodField()

    # DJ-only
    talent_level = serializers.CharField(source='talent.talent_level', read_only=True)
    talent_rating = serializers.DecimalField(
        source='talent.rating_avg', max_digits=3, decimal_places=2, read_only=True
    )
    talent_reviews = serializers.IntegerField(source='talent.total_reviews', read_only=True)

    # Pack-only
    pack_name = serializers.CharField(source='pack.name', read_only=True)
    pack_id = serializers.IntegerField(source='pack.id', read_only=True)

    # Aliases legacy para no romper el frontend viejo
    talent_name = serializers.SerializerMethodField()
    talent_avatar = serializers.SerializerMethodField()
    talent_city = serializers.SerializerMethodField()
    talent_user_id = serializers.SerializerMethodField()

    class Meta:
        model = GigOffer
        fields = [
            'id', 'request', 'offer_kind', 'covers_item',
            'talent', 'partner', 'pack', 'pack_id', 'pack_name',
            'provider_name', 'provider_avatar', 'provider_city', 'provider_user_id',
            'talent_level', 'talent_rating', 'talent_reviews',
            'talent_name', 'talent_avatar', 'talent_city', 'talent_user_id',
            'quoted_price', 'message', 'status',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'request', 'offer_kind', 'talent', 'partner', 'pack',
            'status', 'created_at', 'updated_at',
        ]

    def _provider_user(self, obj):
        if obj.talent_id:
            return obj.talent.user
        return obj.partner

    def get_provider_name(self, obj):
        if obj.talent_id:
            return obj.talent.stage_name
        if obj.partner_id:
            u = obj.partner
            return u.get_full_name() or u.username
        return ''

    def get_provider_avatar(self, obj):
        u = self._provider_user(obj)
        if u and getattr(u, 'avatar', None):
            try:
                return u.avatar.url
            except Exception:
                return None
        return None

    def get_provider_city(self, obj):
        if obj.talent_id:
            return obj.talent.city
        return ''

    def get_provider_user_id(self, obj):
        u = self._provider_user(obj)
        return u.id if u else None

    # Aliases legacy
    def get_talent_name(self, obj): return self.get_provider_name(obj)
    def get_talent_avatar(self, obj): return self.get_provider_avatar(obj)
    def get_talent_city(self, obj): return self.get_provider_city(obj)
    def get_talent_user_id(self, obj): return self.get_provider_user_id(obj)


class GigOfferCreateSerializer(serializers.ModelSerializer):
    """
    Para DJs: envían { quoted_price, message }.
    Para aliados: envían { quoted_price, message, pack_id (opcional), covers_item }.
    """
    pack_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = GigOffer
        fields = ['quoted_price', 'message', 'pack_id', 'covers_item']

    def validate_quoted_price(self, value):
        if value is None or value <= 0:
            raise serializers.ValidationError('El precio debe ser mayor a 0.')
        return value

    def validate_covers_item(self, value):
        if not value:
            return value
        allowed = {k for k, _ in OpenGigRequest.REQUESTED_ITEM_CHOICES}
        if value not in allowed:
            raise serializers.ValidationError(f'Categoría inválida. Debe ser una de: {sorted(allowed)}')
        return value


class OpenGigRequestListSerializer(serializers.ModelSerializer):
    """Vista compacta — para el feed del DJ/aliado y la lista del cliente."""
    client_name = serializers.SerializerMethodField()
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    requested_items_display = serializers.ReadOnlyField()
    offers_count = serializers.SerializerMethodField()
    my_offer_id = serializers.SerializerMethodField()

    class Meta:
        model = OpenGigRequest
        fields = [
            'id', 'client', 'client_name',
            'event_type', 'event_type_display', 'event_name',
            'event_date', 'event_time_start', 'event_time_end',
            'event_duration_hours', 'event_location', 'event_city',
            'event_indoor', 'guest_count', 'genre_preference',
            'requested_items', 'requested_items_display',
            'budget', 'status', 'visible_to_tier',
            'expires_at', 'created_at',
            'offers_count', 'my_offer_id',
        ]

    def get_client_name(self, obj):
        return obj.client.get_full_name() or obj.client.username

    def get_offers_count(self, obj):
        return obj.offers.filter(status='pending').count()

    def get_my_offer_id(self, obj):
        """Devuelve el offer_id del usuario autenticado si ya ofertó."""
        req = self.context.get('request')
        if not req or not req.user.is_authenticated:
            return None
        talent = getattr(req.user, 'talent_profile', None)
        if talent:
            offer = obj.offers.filter(talent=talent).first()
            if offer:
                return offer.id
        # Partner: cualquiera de sus ofertas
        offer = obj.offers.filter(partner=req.user).first()
        return offer.id if offer else None


class OpenGigRequestDetailSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    requested_items_display = serializers.ReadOnlyField()
    offers = serializers.SerializerMethodField()

    class Meta:
        model = OpenGigRequest
        fields = [
            'id', 'client', 'client_name',
            'event_type', 'event_type_display', 'event_name',
            'event_date', 'event_time_start', 'event_time_end',
            'event_duration_hours', 'event_location', 'event_city',
            'event_indoor', 'guest_count', 'description', 'genre_preference',
            'requested_items', 'requested_items_display',
            'additional_services', 'additional_services_notes',
            'budget', 'status', 'visible_to_tier',
            'expires_at', 'assigned_booking',
            'created_at', 'updated_at',
            'offers',
        ]

    def get_client_name(self, obj):
        return obj.client.get_full_name() or obj.client.username

    def get_offers(self, obj):
        """
        El cliente ve todas las ofertas de su request.
        Un DJ solo ve su propia oferta.
        Un aliado ve sus propias ofertas.
        """
        req = self.context.get('request')
        if not req or not req.user.is_authenticated:
            return []
        qs = obj.offers.all().select_related('talent', 'talent__user', 'partner', 'pack')
        if req.user.id == obj.client_id:
            return GigOfferSerializer(qs, many=True, context=self.context).data
        talent = getattr(req.user, 'talent_profile', None)
        if talent:
            qs = qs.filter(talent=talent)
            return GigOfferSerializer(qs, many=True, context=self.context).data
        # Partner
        qs = qs.filter(partner=req.user)
        return GigOfferSerializer(qs, many=True, context=self.context).data


class OpenGigRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpenGigRequest
        fields = [
            'event_type', 'event_name', 'event_date',
            'event_time_start', 'event_time_end', 'event_duration_hours',
            'event_location', 'event_city', 'event_indoor',
            'guest_count', 'description', 'genre_preference',
            'requested_items',
            'additional_services', 'additional_services_notes',
            'budget',
        ]

    def validate_requested_items(self, value):
        if not value:
            raise serializers.ValidationError('Elige al menos un ítem (DJ, sonido, luces, etc.).')
        allowed = {k for k, _ in OpenGigRequest.REQUESTED_ITEM_CHOICES}
        invalid = [v for v in value if v not in allowed]
        if invalid:
            raise serializers.ValidationError(f'Items inválidos: {invalid}. Permitidos: {sorted(allowed)}')
        # de-duplicar preservando orden
        seen, out = set(), []
        for v in value:
            if v not in seen:
                seen.add(v)
                out.append(v)
        return out

    def create(self, validated_data):
        from django.utils import timezone
        from datetime import timedelta
        from .models import PlatformConfig

        user = self.context['request'].user
        validated_data['client'] = user

        cfg = PlatformConfig.get_config()
        pro_delay = getattr(cfg, 'open_gig_pro_delay_minutes', 3) or 3
        std_delay = getattr(cfg, 'open_gig_standard_delay_minutes', 6) or 6
        expiry_hours = getattr(cfg, 'open_gig_expiry_hours', 24) or 24

        now = timezone.now()
        # Si NO se pide DJ, no hay tier staging (los aliados no tienen tiers)
        needs_dj = 'dj' in (validated_data.get('requested_items') or [])
        validated_data['visible_to_tier'] = 'premium' if needs_dj else 'all'
        validated_data['notify_pro_at'] = now + timedelta(minutes=pro_delay) if needs_dj else None
        validated_data['notify_standard_at'] = now + timedelta(minutes=std_delay) if needs_dj else None
        validated_data['expires_at'] = now + timedelta(hours=expiry_hours)

        return OpenGigRequest.objects.create(**validated_data)
