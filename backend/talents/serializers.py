from rest_framework import serializers
from accounts.serializers import UserSerializer
from .models import Genre, TalentProfile, TalentMedia, TalentExperience, Availability


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
    avatar = serializers.ImageField(source='user.avatar', read_only=True)
    media_count = serializers.SerializerMethodField()

    class Meta:
        model = TalentProfile
        fields = [
            'id', 'user_name', 'avatar', 'talent_type', 'talent_level',
            'stage_name', 'genres', 'tagline', 'city', 'country',
            'experience_years', 'hourly_rate',
            'price_min', 'price_max', 'price_currency',
            'rating_avg', 'total_reviews', 'total_bookings',
            'cover_photo', 'is_featured', 'is_approved', 'is_available',
            'media_count'
        ]

    def get_media_count(self, obj):
        return obj.media.count()


class TalentDetailSerializer(serializers.ModelSerializer):
    """Full serializer for talent profile detail."""

    user = UserSerializer(read_only=True)
    genres = GenreSerializer(many=True, read_only=True)
    media = TalentMediaSerializer(many=True, read_only=True)
    experiences = TalentExperienceSerializer(many=True, read_only=True)
    availability = AvailabilitySerializer(many=True, read_only=True)
    genre_ids = serializers.PrimaryKeyRelatedField(
        source='genres', queryset=Genre.objects.all(),
        many=True, write_only=True, required=False
    )

    class Meta:
        model = TalentProfile
        fields = [
            'id', 'user', 'talent_type', 'talent_level', 'stage_name',
            'genres', 'genre_ids',
            'tagline', 'description', 'experience_years',
            'hourly_rate', 'price_min', 'price_max', 'price_currency',
            'equipment_own', 'equipment_description',
            'cover_photo', 'city', 'country', 'latitude', 'longitude',
            'rating_avg', 'total_reviews', 'total_bookings',
            'is_featured', 'is_approved', 'is_available',
            'website', 'instagram', 'soundcloud', 'mixcloud', 'spotify', 'youtube',
            'media', 'experiences', 'availability',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'rating_avg', 'total_reviews', 'total_bookings',
            'is_featured', 'is_approved', 'created_at', 'updated_at'
        ]


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
            'experience_years', 'hourly_rate',
            'price_min', 'price_max', 'price_currency',
            'equipment_own', 'equipment_description', 'cover_photo',
            'city', 'country', 'latitude', 'longitude',
            'is_available', 'website', 'instagram',
            'soundcloud', 'mixcloud', 'spotify', 'youtube'
        ]

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
