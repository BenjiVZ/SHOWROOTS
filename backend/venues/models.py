from django.db import models


class Venue(models.Model):
    """A venue/location where events can be held."""

    VENUE_TYPE_CHOICES = [
        ('salon', 'Salón de Eventos'),
        ('hotel', 'Hotel'),
        ('restaurant', 'Restaurante'),
        ('club', 'Club/Discoteca'),
        ('outdoor', 'Al Aire Libre'),
        ('beach', 'Playa'),
        ('rooftop', 'Rooftop/Terraza'),
        ('hacienda', 'Hacienda/Finca'),
        ('other', 'Otro'),
    ]

    PRICE_RANGE_CHOICES = [
        ('$', 'Económico'),
        ('$$', 'Moderado'),
        ('$$$', 'Premium'),
        ('$$$$', 'Lujo'),
    ]

    name = models.CharField(max_length=200)
    venue_type = models.CharField(max_length=20, choices=VENUE_TYPE_CHOICES)
    description = models.TextField(blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=50, default='Venezuela')
    capacity_min = models.PositiveIntegerField(default=0)
    capacity_max = models.PositiveIntegerField(default=0)
    price_range = models.CharField(max_length=4, choices=PRICE_RANGE_CHOICES, default='$$')
    amenities = models.JSONField(default=list, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    instagram = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    cover_photo = models.ImageField(upload_to='venues/covers/', blank=True, null=True)
    rating_avg = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'venues'
        ordering = ['-is_verified', '-rating_avg', 'name']
        verbose_name = 'Local'
        verbose_name_plural = 'Locales'

    def __str__(self):
        return f"{self.name} ({self.city})"


class VenuePhoto(models.Model):
    """Photos of a venue."""

    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to='venues/photos/')
    caption = models.CharField(max_length=200, blank=True)
    is_cover = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'venue_photos'
        ordering = ['order']
        verbose_name = 'Foto del local'
        verbose_name_plural = 'Fotos del local'

    def __str__(self):
        return f"{self.venue.name} - Foto #{self.order}"
