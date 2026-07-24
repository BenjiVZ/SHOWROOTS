from django.contrib import admin

from unfold.admin import ModelAdmin, TabularInline

from .models import Venue, VenuePhoto


class VenuePhotoInline(TabularInline):
    model = VenuePhoto
    extra = 0


@admin.register(Venue)
class VenueAdmin(ModelAdmin):
    list_display = [
        'name', 'venue_type', 'city', 'capacity_min', 'capacity_max',
        'price_range', 'rating_avg', 'is_verified', 'is_active'
    ]
    list_filter = ['venue_type', 'city', 'price_range', 'is_verified', 'is_active']
    search_fields = ['name', 'city', 'address']
    inlines = [VenuePhotoInline]
