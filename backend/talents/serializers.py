from rest_framework import serializers
from accounts.serializers import UserSerializer
from .models import Genre, TalentProfile, TalentMedia, TalentExperience, Availability, Pack, TalentFAQ


class PackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pack
        fields = [
            'id', 'talent', 'name', 'price', 'price_label', 'duration_hours',
            'currency', 'included_items', 'is_featured', 'order',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'talent', 'created_at', 'updated_at']


class TalentFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = TalentFAQ
        fields = ['id', 'talent', 'question', 'answer', 'order', 'created_at']
        read_only_fields = ['id', 'talent', 'created_at']


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name', 'slug', 'icon']


class TalentMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TalentMedia
        fields = [
            'id', 'media_type', 'file', 'url', 'title',
            'description', 'thumbnail', 'is_cover', 'order', 'created_at'
        ]

    def _url(self, file_field):
        """Devuelve URL relativa (/media/...) — el frontend la resuelve vía proxy."""
        if not file_field:
            return None
        try:
            return file_field.url
        except Exception:
            return None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['file'] = self._url(instance.file)
        data['thumbnail'] = self._url(instance.thumbnail)
        return data


class TalentExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TalentExperience
        fields = ['id', 'event_name', 'venue_name', 'date', 'description', 'photo']


class AvailabilitySerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Availability
        fields = [
            'id', 'talent', 'date', 'time_start', 'time_end',
            'status', 'status_display', 'note', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AvailabilityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = ['date', 'time_start', 'time_end', 'status', 'note']

    def create(self, validated_data):
        talent = self.context['talent']
        availability, created = Availability.objects.update_or_create(
            talent=talent,
            date=validated_data['date'],
            defaults=validated_data
        )
        return availability


class TalentListSerializer(serializers.ModelSerializer):
    """Compact serializer for listing talents."""

    genres = GenreSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    avatar = serializers.SerializerMethodField()
    cover_photo = serializers.SerializerMethodField()
    media_count = serializers.SerializerMethodField()

    class Meta:
        model = TalentProfile
        fields = [
            'id', 'user_name', 'avatar', 'talent_type', 'talent_level',
            'stage_name', 'genres', 'tagline', 'city', 'country',
            'experience_years', 'experience_level', 'hourly_rate',
            'price_min', 'price_max', 'price_currency',
            'rating_avg', 'total_reviews', 'total_bookings',
            'cover_photo', 'is_featured', 'is_approved', 'is_available',
            'coverage_radius_km', 'onboarding_completed', 'media_count'
        ]

    def _url(self, file_field):
        """URL relativa (/media/...) — funciona con cualquier dominio gracias al proxy."""
        if not file_field:
            return None
        try:
            return file_field.url
        except Exception:
            return None

    def get_avatar(self, obj):
        return self._url(obj.user.avatar) if obj.user else None

    def get_cover_photo(self, obj):
        return self._url(obj.cover_photo)

    def get_media_count(self, obj):
        return obj.media.count()


class TalentDetailSerializer(serializers.ModelSerializer):
    """Full serializer for talent profile detail."""

    user = UserSerializer(read_only=True)
    genres = GenreSerializer(many=True, read_only=True)
    media = TalentMediaSerializer(many=True, read_only=True)
    experiences = TalentExperienceSerializer(many=True, read_only=True)
    availability = AvailabilitySerializer(many=True, read_only=True)
    packs = PackSerializer(many=True, read_only=True)
    faqs = TalentFAQSerializer(many=True, read_only=True)
    cover_photo = serializers.SerializerMethodField()
    response_time_hours = serializers.SerializerMethodField()
    repeat_rate = serializers.SerializerMethodField()
    genre_ids = serializers.PrimaryKeyRelatedField(
        source='genres', queryset=Genre.objects.all(),
        many=True, write_only=True, required=False
    )

    def get_response_time_hours(self, obj):
        """Promedio en horas entre booking creado y primer mensaje del talento."""
        from bookings.models import Message
        from django.db.models import F
        durations = []
        bookings = obj.bookings.exclude(status='solicitud_enviada').only('id', 'created_at')[:30]
        for b in bookings:
            first_msg = Message.objects.filter(
                booking=b, sender=obj.user
            ).order_by('created_at').first()
            if first_msg:
                delta = first_msg.created_at - b.created_at
                durations.append(delta.total_seconds() / 3600)
        if not durations:
            return None
        return round(sum(durations) / len(durations), 1)

    def get_repeat_rate(self, obj):
        """% de clientes que reservaron al talento más de una vez."""
        completed = obj.bookings.filter(status='completada')
        if completed.count() < 2:
            return None
        from django.db.models import Count
        clients_with_counts = completed.values('client_id').annotate(c=Count('id'))
        total = clients_with_counts.count()
        repeats = sum(1 for row in clients_with_counts if row['c'] > 1)
        if total == 0:
            return None
        return round(repeats * 100 / total, 0)

    class Meta:
        model = TalentProfile
        fields = [
            'id', 'user', 'talent_type', 'talent_level', 'stage_name',
            'genres', 'genre_ids',
            'tagline', 'description', 'experience_years', 'experience_level',
            'hourly_rate', 'price_min', 'price_max', 'price_currency',
            'equipment_own', 'equipment_description',
            'equipment_brings', 'equipment_not_included',
            'service_zones', 'travel_fee_extra',
            'cover_photo', 'city', 'country', 'latitude', 'longitude',
            'coverage_radius_km', 'mood_tags', 'event_types', 'languages',
            'rating_avg', 'total_reviews', 'total_bookings',
            'response_time_hours', 'repeat_rate',
            'is_featured', 'is_approved', 'is_available', 'onboarding_completed',
            'website', 'instagram', 'tiktok', 'soundcloud', 'mixcloud', 'spotify', 'youtube',
            'media', 'experiences', 'availability', 'packs', 'faqs',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'rating_avg', 'total_reviews', 'total_bookings',
            'is_featured', 'is_approved', 'created_at', 'updated_at'
        ]

    def get_cover_photo(self, obj):
        if not obj.cover_photo:
            return None
        try:
            return obj.cover_photo.url
        except Exception:
            return None


class TalentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating a talent profile."""

    genre_ids = serializers.PrimaryKeyRelatedField(
        source='genres', queryset=Genre.objects.all(),
        many=True, required=False
    )

    class Meta:
        model = TalentProfile
        fields = [
            'talent_type', 'stage_name', 'genre_ids', 'tagline', 'description',
            'experience_years', 'experience_level', 'hourly_rate',
            'price_min', 'price_max', 'price_currency',
            'equipment_own', 'equipment_description',
            'equipment_brings', 'equipment_not_included',
            'service_zones', 'travel_fee_extra', 'cover_photo',
            'city', 'country', 'latitude', 'longitude',
            'coverage_radius_km', 'mood_tags', 'event_types', 'languages',
            'onboarding_completed',
            'is_available', 'website', 'instagram', 'tiktok',
            'soundcloud', 'mixcloud', 'spotify', 'youtube'
        ]

    def validate_description(self, value):
        """Enforce bio length por tier — solo aplica si ya hay perfil con tier."""
        from .tier_limits import get_limits
        instance = self.instance
        if instance:
            limits = get_limits(instance.talent_level)
            max_chars = limits.get('max_bio_chars')
            if max_chars and value and len(value) > max_chars:
                raise serializers.ValidationError(
                    f'Tu tier {instance.get_talent_level_display()} permite máximo {max_chars} caracteres en bio. '
                    f'Tienes {len(value)}. Sube de tier o reduce el texto.'
                )
        return value

    def create(self, validated_data):
        genres = validated_data.pop('genres', [])
        validated_data['user'] = self.context['request'].user
        profile = TalentProfile.objects.create(**validated_data)
        profile.genres.set(genres)
        return profile

    def update(self, instance, validated_data):
        genres = validated_data.pop('genres', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if genres is not None:
            instance.genres.set(genres)
        return instance
