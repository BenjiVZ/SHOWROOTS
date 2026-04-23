from django.contrib import admin
from .models import Genre, TalentProfile, TalentMedia, TalentExperience, Availability


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon']
    prepopulated_fields = {'slug': ('name',)}


class TalentMediaInline(admin.TabularInline):
    model = TalentMedia
    extra = 0
    fields = ['media_type', 'title', 'file', 'url', 'order']


class TalentExperienceInline(admin.TabularInline):
    model = TalentExperience
    extra = 0


class AvailabilityInline(admin.TabularInline):
    model = Availability
    extra = 0
    fields = ['date', 'time_start', 'time_end', 'status', 'note']


@admin.register(TalentProfile)
class TalentProfileAdmin(admin.ModelAdmin):
    list_display = [
        'stage_name', 'user', 'talent_type', 'talent_level',
        'hourly_rate', 'city', 'rating_avg', 'total_bookings',
        'is_approved', 'is_featured', 'is_available'
    ]
    list_filter = ['talent_type', 'talent_level', 'is_approved', 'is_featured', 'is_available', 'country']
    search_fields = ['stage_name', 'user__first_name', 'user__last_name', 'city']
    list_editable = ['talent_level', 'is_approved', 'is_featured']
    inlines = [TalentMediaInline, TalentExperienceInline, AvailabilityInline]
    fieldsets = (
        ('Información básica', {
            'fields': ('user', 'talent_type', 'talent_level', 'stage_name', 'tagline', 'description')
        }),
        ('Ubicación', {
            'fields': ('city', 'country', 'latitude', 'longitude')
        }),
        ('Precios', {
            'fields': ('hourly_rate', 'price_min', 'price_max', 'price_currency')
        }),
        ('Experiencia y equipo', {
            'fields': ('experience_years', 'equipment_own', 'equipment_description')
        }),
        ('Estado', {
            'fields': ('is_approved', 'is_featured', 'is_available', 'rating_avg', 'total_reviews', 'total_bookings')
        }),
        ('Redes sociales', {
            'fields': ('website', 'instagram', 'soundcloud', 'mixcloud', 'spotify', 'youtube'),
            'classes': ('collapse',)
        }),
        ('Géneros y media', {
            'fields': ('genres', 'cover_photo')
        }),
    )
    readonly_fields = ['rating_avg', 'total_reviews', 'total_bookings']


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ['talent', 'date', 'status', 'note']
    list_filter = ['status', 'date']
    search_fields = ['talent__stage_name']
