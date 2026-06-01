from django.db import models
from django.conf import settings


class Genre(models.Model):
    """Musical genre for talent categorization."""

    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    icon = models.CharField(max_length=10, blank=True, help_text='Emoji icon')

    class Meta:
        db_table = 'genres'
        ordering = ['name']
        verbose_name = 'Género musical'
        verbose_name_plural = 'Géneros musicales'

    def __str__(self):
        return self.name


class TalentProfile(models.Model):
    """Profile for a DJ, musician, or band."""

    TALENT_TYPE_CHOICES = [
        ('dj', 'DJ'),
        ('musician', 'Músico'),
        ('band', 'Banda'),
    ]

    TALENT_LEVEL_CHOICES = [
        ('standard', 'Standard'),
        ('pro', 'Pro'),
        ('premium', 'Premium'),
    ]

    EXPERIENCE_LEVEL_CHOICES = [
        ('beginner', 'Principiante'),
        ('semi_professional', 'Semiprofesional'),
        ('professional', 'Profesional'),
        ('expert', 'Experto'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='talent_profile'
    )
    talent_type = models.CharField(max_length=10, choices=TALENT_TYPE_CHOICES)
    talent_level = models.CharField(
        max_length=10, choices=TALENT_LEVEL_CHOICES, default='standard',
        help_text='Nivel del talento: standard o premium'
    )
    stage_name = models.CharField(max_length=100, help_text='Nombre artístico')
    genres = models.ManyToManyField(Genre, blank=True, related_name='talents')
    tagline = models.CharField(max_length=200, blank=True, help_text='Frase corta descriptiva')
    description = models.TextField(blank=True, help_text='Descripción detallada')
    experience_years = models.PositiveIntegerField(default=0)
    hourly_rate = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text='Tarifa por hora (USD)'
    )
    price_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_currency = models.CharField(max_length=3, default='USD')
    equipment_own = models.BooleanField(default=False, help_text='¿Tiene equipo propio?')
    equipment_description = models.TextField(blank=True)
    cover_photo = models.ImageField(upload_to='talents/covers/', blank=True, null=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=50, default='Venezuela')
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    rating_avg = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    total_bookings = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_approved = models.BooleanField(
        default=False,
        help_text='Admin debe aprobar antes de que sea visible'
    )
    is_available = models.BooleanField(default=True)
    experience_level = models.CharField(
        max_length=20, choices=EXPERIENCE_LEVEL_CHOICES,
        default='beginner', help_text='Nivel de experiencia del talento'
    )
    coverage_radius_km = models.PositiveIntegerField(
        default=50, help_text='Radio de cobertura en km desde su ubicación'
    )
    onboarding_completed = models.BooleanField(
        default=False, help_text='Si el talento completó el wizard de onboarding'
    )
    mood_tags = models.JSONField(
        default=list, blank=True,
        help_text='Lista de moods/vibes (ej: ["Boda elegante", "After party", "Cocktail formal"])'
    )
    event_types = models.JSONField(
        default=list, blank=True,
        help_text='Tipos de eventos que cubre (slugs: wedding, corporate, birthday, cocktail, club, launch)'
    )
    languages = models.JSONField(
        default=list, blank=True,
        help_text='Idiomas en los que puede hacer MC (ej: ["Español", "Inglés"])'
    )
    equipment_brings = models.JSONField(
        default=list, blank=True,
        help_text='Equipamiento que el talento trae (ej: ["2x CDJ-3000", "Mixer DJM-A9", "Auriculares"])'
    )
    equipment_not_included = models.JSONField(
        default=list, blank=True,
        help_text='Equipamiento NO incluido (ej: ["Sonido +80 personas", "Luces", "Pantallas"])'
    )
    service_zones = models.JSONField(
        default=list, blank=True,
        help_text='Zonas/barrios específicos de cobertura (ej: ["Casco Antiguo", "Costa del Este", "Coronado"])'
    )
    travel_fee_extra = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        help_text='Cargo adicional por traslado fuera del área de cobertura'
    )
    recommended_partners = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='recommended_by_talents',
        help_text='Aliados de producción recomendados por este DJ (aparecen primero en su booking flow)'
    )
    website = models.URLField(blank=True)
    instagram = models.CharField(max_length=100, blank=True)
    tiktok = models.CharField(max_length=100, blank=True)
    soundcloud = models.URLField(blank=True)
    mixcloud = models.URLField(blank=True)
    spotify = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'talent_profiles'
        verbose_name = 'Perfil de talento'
        verbose_name_plural = 'Perfiles de talento'
        # Premium first, then featured, then by rating
        ordering = [
            models.Case(
                models.When(talent_level='premium', then=0),
                default=1,
                output_field=models.IntegerField(),
            ),
            '-is_featured',
            '-rating_avg',
            '-created_at',
        ]

    def __str__(self):
        return f"{self.stage_name} ({self.get_talent_type_display()}) [{self.talent_level}]"


class TalentMedia(models.Model):
    """Photos, videos, audio, and links for a talent profile."""

    MEDIA_TYPE_CHOICES = [
        ('photo', 'Foto'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('link', 'Link'),
    ]

    talent = models.ForeignKey(
        TalentProfile,
        on_delete=models.CASCADE,
        related_name='media'
    )
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    file = models.FileField(upload_to='talents/media/', blank=True, null=True)
    url = models.URLField(blank=True, help_text='YouTube, SoundCloud, Mixcloud URL')
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to='talents/thumbnails/', blank=True, null=True)
    is_cover = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'talent_media'
        ordering = ['order', '-created_at']
        verbose_name = 'Media del talento'
        verbose_name_plural = 'Media del talento'

    def __str__(self):
        return f"{self.talent.stage_name} - {self.title or self.get_media_type_display()}"


class TalentExperience(models.Model):
    """Past events and experience for a talent."""

    talent = models.ForeignKey(
        TalentProfile,
        on_delete=models.CASCADE,
        related_name='experiences'
    )
    event_name = models.CharField(max_length=200)
    venue_name = models.CharField(max_length=200, blank=True)
    date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to='talents/experience/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'talent_experiences'
        ordering = ['-date']
        verbose_name = 'Experiencia (evento pasado)'
        verbose_name_plural = 'Experiencias (eventos pasados)'

    def __str__(self):
        return f"{self.talent.stage_name} @ {self.event_name}"


class Availability(models.Model):
    """Talent availability calendar."""

    STATUS_CHOICES = [
        ('available', 'Disponible'),
        ('blocked', 'Bloqueado'),
        ('booked', 'Reservado'),
    ]

    talent = models.ForeignKey(
        TalentProfile,
        on_delete=models.CASCADE,
        related_name='availability'
    )
    date = models.DateField()
    time_start = models.TimeField(null=True, blank=True)
    time_end = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')
    note = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'talent_availability'
        ordering = ['date', 'time_start']
        unique_together = ['talent', 'date']
        verbose_name = 'Disponibilidad'
        verbose_name_plural = 'Disponibilidades'

    def __str__(self):
        return f"{self.talent.stage_name} - {self.date} ({self.get_status_display()})"


class Pack(models.Model):
    """Paquete de servicio pre-armado del talento (ej: Pack Boda $600 / 4h)."""

    talent = models.ForeignKey(
        TalentProfile,
        on_delete=models.CASCADE,
        related_name='packs'
    )
    name = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_label = models.CharField(
        max_length=40, blank=True,
        help_text='Texto alternativo cuando no hay precio fijo (ej: "Cotizar")'
    )
    duration_hours = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True,
        help_text='Duración en horas (ej: 4.0)'
    )
    currency = models.CharField(max_length=3, default='USD')
    included_items = models.JSONField(
        default=list, blank=True,
        help_text='Items incluidos (ej: ["DJ + sonido básico", "Micrófono", "Setlist"])'
    )
    is_featured = models.BooleanField(default=False, help_text='Marcar como "POPULAR" en el perfil')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'talent_packs'
        ordering = ['order', 'price']
        verbose_name = 'Paquete del talento'
        verbose_name_plural = 'Paquetes del talento'

    def __str__(self):
        return f"{self.talent.stage_name} · {self.name}"


class TalentFAQ(models.Model):
    """Preguntas frecuentes personalizadas del talento."""

    talent = models.ForeignKey(
        TalentProfile,
        on_delete=models.CASCADE,
        related_name='faqs'
    )
    question = models.CharField(max_length=255)
    answer = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'talent_faqs'
        ordering = ['order', 'created_at']
        verbose_name = 'FAQ del talento'
        verbose_name_plural = 'FAQs del talento'

    def __str__(self):
        return f"{self.talent.stage_name} · {self.question[:50]}"
