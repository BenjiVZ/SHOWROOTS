from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model with roles for the Pulsar marketplace."""

    ROLE_CHOICES = [
        ('talent', 'Talento'),
        ('client', 'Cliente'),
        ('admin', 'Administrador'),
        ('partner', 'Aliado'),
    ]

    role = models.CharField('Rol principal', max_length=10, choices=ROLE_CHOICES, default='client')
    avatar = models.ImageField('Foto de perfil', upload_to='avatars/', blank=True, null=True)
    phone = models.CharField('Teléfono', max_length=20, blank=True)
    city = models.CharField('Ciudad', max_length=100, blank=True)
    country = models.CharField('País', max_length=50, default='Venezuela')
    bio = models.TextField('Biografía', blank=True)
    is_verified = models.BooleanField('Verificado', default=False)
    # ── Roles secundarios (multi-rol simultáneo) ──
    is_partner_active = models.BooleanField(
        'Rol Aliado activo',
        default=False,
        help_text='Si el usuario tiene el rol Aliado activo (puede ser además de Talento/Cliente)'
    )
    partner_offers = models.JSONField(
        'Ofertas del Aliado',
        default=list, blank=True,
        help_text='Qué ofrece el Aliado. Valores: "referral" (trae clientes), "packs" (renta producción), "venue" (espacio físico)'
    )
    discovery_source = models.CharField(
        '¿Cómo nos conoció?',
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
    created_at = models.DateTimeField('Fecha de registro', auto_now_add=True)
    updated_at = models.DateTimeField('Última actualización', auto_now=True)
    last_seen_at = models.DateTimeField(
        'Última actividad', null=True, blank=True,
        help_text='Última vez que el usuario hizo una petición autenticada. Usado para decidir si notificar por email.'
    )

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
