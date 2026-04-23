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
        ('premium', 'Premium'),
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
    website = models.URLField(blank=True)
    instagram = models.CharField(max_length=100, blank=True)
    soundcloud = models.URLField(blank=True)
    mixcloud = models.URLField(blank=True)
    spotify = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'talent_profiles'
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

    def __str__(self):
        return f"{self.talent.stage_name} - {self.date} ({self.get_status_display()})"
