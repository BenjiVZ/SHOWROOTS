from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with roles for the Pulsar marketplace."""

    ROLE_CHOICES = [
        ('talent', 'Talento'),
        ('client', 'Cliente'),
        ('admin', 'Administrador'),
        ('partner', 'Partner'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='client')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=50, default='Venezuela')
    bio = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    discovery_source = models.CharField(
        max_length=20, blank=True,
        choices=[
            ('friend', 'Amigo o colega'),
            ('search_engine', 'Buscadores'),
            ('social_media', 'Redes sociales'),
            ('website', 'Sitio web o blog'),
            ('event', 'Evento o showcase'),
            ('other', 'Otro'),
        ],
        help_text='¿Cómo descubriste Pulsar?'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
