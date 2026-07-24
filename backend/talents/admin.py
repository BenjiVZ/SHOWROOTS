from django.contrib import admin

from unfold.admin import ModelAdmin, TabularInline

from .models import Genre, TalentProfile, TalentMedia, TalentExperience, Availability


@admin.register(Genre)
class GenreAdmin(ModelAdmin):
    list_display = ['name', 'slug', 'icon']
    prepopulated_fields = {'slug': ('name',)}


class TalentMediaInline(TabularInline):
    model = TalentMedia
    extra = 0
    fields = ['media_type', 'title', 'file', 'url', 'order']


class TalentExperienceInline(TabularInline):
    model = TalentExperience
    extra = 0


class AvailabilityInline(TabularInline):
    model = Availability
    extra = 0
    fields = ['date', 'time_start', 'time_end', 'status', 'note']


@admin.register(TalentProfile)
class TalentProfileAdmin(ModelAdmin):
    list_display = [
        'stage_name', 'user', 'talent_type', 'talent_level',
        'hourly_rate', 'city', 'rating_avg', 'total_bookings',
        'is_approved', 'is_featured', 'is_available'
    ]
    list_filter = ['talent_type', 'talent_level', 'is_approved', 'is_featured', 'is_available', 'country']
    search_fields = ['stage_name', 'user__first_name', 'user__last_name', 'city']
    list_editable = ['talent_level', 'is_approved', 'is_featured']
    actions = ['approve_talents', 'feature_talents', 'unfeature_talents']
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

    @admin.action(description='Aprobar talentos seleccionados')
    def approve_talents(self, request, queryset):
        n = queryset.update(is_approved=True)
        self.message_user(request, f'{n} talento(s) aprobados.')

    @admin.action(description='Destacar (featured)')
    def feature_talents(self, request, queryset):
        n = queryset.update(is_featured=True)
        self.message_user(request, f'{n} talento(s) destacados.')

    @admin.action(description='Quitar destacado')
    def unfeature_talents(self, request, queryset):
        n = queryset.update(is_featured=False)
        self.message_user(request, f'{n} talento(s) sin destacar.')


@admin.register(Availability)
class AvailabilityAdmin(ModelAdmin):
    list_display = ['talent', 'date', 'status', 'note']
    list_filter = ['status', 'date']
    search_fields = ['talent__stage_name']
