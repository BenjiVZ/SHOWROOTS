from rest_framework import serializers
from .models import Venue, VenuePhoto


class VenuePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenuePhoto
        fields = ['id', 'photo', 'caption', 'is_cover', 'order']


class VenueListSerializer(serializers.ModelSerializer):
    venue_type_display = serializers.CharField(source='get_venue_type_display', read_only=True)
    photo_count = serializers.SerializerMethodField()

    class Meta:
        model = Venue
        fields = [
            'id', 'name', 'venue_type', 'venue_type_display',
            'city', 'state', 'capacity_min', 'capacity_max',
            'price_range', 'cover_photo', 'rating_avg',
            'is_verified', 'photo_count'
        ]

    def get_photo_count(self, obj):
        return obj.photos.count()


class VenueDetailSerializer(serializers.ModelSerializer):
    photos = VenuePhotoSerializer(many=True, read_only=True)
    venue_type_display = serializers.CharField(source='get_venue_type_display', read_only=True)
    price_range_display = serializers.CharField(source='get_price_range_display', read_only=True)

    class Meta:
        model = Venue
        fields = [
            'id', 'name', 'venue_type', 'venue_type_display',
            'description', 'address', 'city', 'state', 'country',
            'capacity_min', 'capacity_max', 'price_range', 'price_range_display',
            'amenities', 'phone', 'email', 'website', 'instagram',
            'latitude', 'longitude', 'cover_photo', 'rating_avg',
            'is_verified', 'photos', 'created_at'
        ]
