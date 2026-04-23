import json
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal


class Booking(models.Model):
    """A booking request from a client to a talent."""

    STATUS_CHOICES = [
        ('solicitud_enviada', 'Solicitud Enviada'),
        ('pendiente_respuesta', 'Pendiente de Respuesta'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
        ('pendiente_pago', 'Pendiente de Pago'),
        ('confirmada', 'Confirmada'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]

    EVENT_TYPE_CHOICES = [
        ('wedding', 'Boda'),
        ('corporate', 'Evento Corporativo'),
        ('birthday', 'Cumpleaños'),
        ('graduation', 'Graduación'),
        ('festival', 'Festival'),
        ('club', 'Club/Discoteca'),
        ('private', 'Fiesta Privada'),
        ('anniversary', 'Aniversario'),
        ('other', 'Otro'),
    ]

    BOOKING_TYPE_CHOICES = [
        ('directa', 'Directa'),
        ('partner', 'Partner'),
    ]

    # Core relationships
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='client_bookings'
    )
    talent = models.ForeignKey(
        'talents.TalentProfile',
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    partner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='partner_bookings',
        help_text='Partner que gestionó esta reserva'
    )

    # Booking type
    booking_type = models.CharField(
        max_length=10, choices=BOOKING_TYPE_CHOICES, default='directa'
    )

    # Event details
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    event_name = models.CharField(max_length=200, blank=True)
    event_date = models.DateField()
    event_time_start = models.TimeField()
    event_time_end = models.TimeField()
    event_duration_hours = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text='Duración del servicio en horas'
    )
    event_location = models.CharField(max_length=300)
    event_city = models.CharField(max_length=100, blank=True)
    event_indoor = models.BooleanField(default=True, help_text='True=Interior, False=Exterior')
    guest_count = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True, help_text='Detalles y requerimientos')
    genre_preference = models.CharField(max_length=100, blank=True, help_text='Genero o ambiente deseado')

    # Additional production services (JSON: [{"service": "sound", "details": {...}}, ...])
    additional_services = models.JSONField(
        default=list, blank=True,
        help_text='Servicios adicionales de producción seleccionados'
    )
    additional_services_notes = models.TextField(
        blank=True, help_text='Notas sobre servicios de producción adicionales'
    )

    # Expiration tracking
    expires_at = models.DateTimeField(
        null=True, blank=True,
        help_text='Fecha de expiración automática de la solicitud'
    )

    # Client final (when Partner books on behalf of someone)
    client_final_name = models.CharField(max_length=200, blank=True, help_text='Nombre del cliente final (si es reserva por Partner)')
    client_final_email = models.EmailField(blank=True, help_text='Email del cliente final')
    client_final_phone = models.CharField(max_length=20, blank=True, help_text='Telefono del cliente final')

    # Pricing
    budget = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        help_text='Presupuesto del cliente'
    )
    precio_estimado = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        help_text='Precio estimado por el sistema (tarifa/hora × duración)'
    )
    quoted_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        help_text='Precio final propuesto por el talento'
    )
    deposit_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('50.00'),
        help_text='Porcentaje requerido como depósito'
    )
    amount_paid = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00'),
        help_text='Monto total pagado hasta ahora'
    )

    # Service fee ("Gestión y garantía") — charged to client
    service_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00'),
        help_text='Fee de gestión y garantía cobrado al cliente'
    )

    # Status & notes
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='solicitud_enviada')
    talent_notes = models.TextField(blank=True, help_text='Notas del talento sobre la cotización')
    client_notes = models.TextField(blank=True, help_text='Notas adicionales del cliente')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bookings'
        ordering = ['-created_at']

    @property
    def is_expired(self):
        """Check if the booking request has expired."""
        if self.expires_at and self.status == 'solicitud_enviada':
            return timezone.now() > self.expires_at
        return False

    def __str__(self):
        return f"Booking #{self.id} - {self.client} → {self.talent} ({self.get_status_display()})"

    def calculate_estimated_price(self):
        """Calculate estimated price based on talent hourly rate and duration."""
        if self.talent.hourly_rate and self.event_duration_hours:
            self.precio_estimado = self.talent.hourly_rate * self.event_duration_hours
            return self.precio_estimado
        return None

    def calculate_service_fee(self):
        """
        Calculate 'Gestión y garantía' fee for the client.
        Uses 5% of event total, or tiered fixed amounts.
        """
        config = PlatformConfig.get_config()
        base = self.final_price or Decimal('0.00')
        if base <= 0:
            self.service_fee = Decimal('0.00')
            return self.service_fee

        if config.service_fee_mode == 'percentage':
            self.service_fee = (base * config.service_fee_rate).quantize(Decimal('0.01'))
        else:  # tiered
            if base <= 400:
                self.service_fee = config.service_fee_small
            elif base <= 800:
                self.service_fee = config.service_fee_medium
            else:
                self.service_fee = config.service_fee_large
        return self.service_fee

    @property
    def final_price(self):
        """The final price is the quoted price if available, otherwise estimated."""
        return self.quoted_price or self.precio_estimado or self.budget

    @property
    def total_client_cost(self):
        """Total that the client pays = event price + service fee."""
        price = self.final_price or Decimal('0.00')
        return price + self.service_fee

    @property
    def remaining_balance(self):
        """Amount still owed (includes service fee)."""
        total = self.total_client_cost
        if total:
            return max(total - self.amount_paid, Decimal('0.00'))
        return Decimal('0.00')


class Payment(models.Model):
    """Payment records for bookings."""

    PAYMENT_TYPE_CHOICES = [
        ('deposit', 'Abono/Depósito'),
        ('full', 'Pago Total'),
        ('balance', 'Saldo Restante'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
        ('refunded', 'Reembolsado'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('card', 'Tarjeta'),
        ('transfer', 'Transferencia'),
        ('paypal', 'PayPal'),
        ('cash', 'Efectivo'),
        ('other', 'Otro'),
    ]

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments_made'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPE_CHOICES)
    payment_status = models.CharField(
        max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending'
    )
    payment_method = models.CharField(
        max_length=10, choices=PAYMENT_METHOD_CHOICES, default='card'
    )
    # Commission breakdown
    commission_showroots = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00'),
        help_text='Comisión para ShowRoots'
    )
    commission_partner = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00'),
        help_text='Comisión para el Partner (si aplica)'
    )
    talent_payout = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00'),
        help_text='Monto neto para el talento'
    )
    # Metadata
    transaction_ref = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment ${self.amount} - Booking #{self.booking_id} ({self.get_payment_status_display()})"

    def calculate_commissions(self, platform_rate=None, partner_rate=None):
        """
        Calculate commission breakdown using configurable rates from PlatformConfig.
        Uses talent level to determine the correct commission rate:
          - Standard: 20% (higher commission, lower visibility)
          - Premium:  15% (lower commission, higher visibility)
        """
        from bookings.models import PlatformConfig
        config = PlatformConfig.get_config()

        # Determine platform commission based on talent level
        if platform_rate is None:
            talent_level = self.booking.talent.talent_level
            if talent_level == 'premium':
                platform_rate = config.premium_commission_rate
            else:
                platform_rate = config.standard_commission_rate

        if partner_rate is None:
            partner_rate = config.partner_commission_rate

        self.commission_showroots = (self.amount * platform_rate).quantize(Decimal('0.01'))
        if self.booking.partner:
            self.commission_partner = (self.commission_showroots * partner_rate).quantize(Decimal('0.01'))
            self.commission_showroots -= self.commission_partner
        self.talent_payout = self.amount - self.commission_showroots - self.commission_partner

    def save(self, *args, **kwargs):
        # Auto-calculate commissions if not set
        if self.talent_payout == Decimal('0.00') and self.amount > 0:
            self.calculate_commissions()
        super().save(*args, **kwargs)
        # Update booking amount_paid if payment is completed
        if self.payment_status == 'completed':
            booking = self.booking
            total_paid = Payment.objects.filter(
                booking=booking, payment_status='completed'
            ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
            booking.amount_paid = total_paid
            # Auto-confirm booking if paid
            if booking.status == 'pendiente_pago':
                booking.status = 'confirmada'
            booking.save(update_fields=['amount_paid', 'status', 'updated_at'])


class Message(models.Model):
    """Chat messages between client and talent within a booking."""

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content = models.TextField()
    file_url = models.URLField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'messages'
        ordering = ['created_at']

    def __str__(self):
        return f"Msg from {self.sender} on Booking #{self.booking_id}"


class Notification(models.Model):
    """In-platform notifications for users."""

    TYPE_CHOICES = [
        ('new_request', 'Nueva Solicitud'),
        ('request_accepted', 'Solicitud Aceptada'),
        ('request_rejected', 'Solicitud Rechazada'),
        ('payment_received', 'Pago Recibido'),
        ('booking_confirmed', 'Reserva Confirmada'),
        ('booking_completed', 'Reserva Completada'),
        ('new_review', 'Nueva Reseña'),
        ('new_message', 'Nuevo Mensaje'),
        ('reminder', 'Recordatorio'),
        ('system', 'Sistema'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=300, blank=True, help_text='URL interna')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} → {self.user}"


class Review(models.Model):
    """Review from a client after an event."""

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_given'
    )
    talent = models.ForeignKey(
        'talents.TalentProfile',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reviews'
        ordering = ['-created_at']

    def __str__(self):
        return f"Review {self.rating}★ - {self.client} → {self.talent}"

    def save(self, *args, **kwargs):
        # Only allow reviews on completed bookings
        if self.booking.status != 'completada':
            raise ValueError('Solo se pueden dejar reseñas en reservas completadas.')
        super().save(*args, **kwargs)
        # Update talent's average rating
        from talents.models import TalentProfile
        talent = self.talent
        reviews = Review.objects.filter(talent=talent)
        talent.rating_avg = reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0
        talent.total_reviews = reviews.count()
        talent.save(update_fields=['rating_avg', 'total_reviews'])


class PlatformConfig(models.Model):
    """
    Singleton configuration for platform-wide settings.

    Commission model:
      - Standard talent: 20% commission (higher commission, lower visibility)
      - Premium talent:  15% commission (lower commission, higher visibility)
      - Partner: receives 30% of the platform commission

    Service fee ('Gestión y garantía') charged to client:
      - percentage mode: 5% of event total
      - tiered mode: $10-15 (small), $15-20 (medium), $20-30 (large)
    """

    SERVICE_FEE_MODE_CHOICES = [
        ('percentage', 'Porcentaje del total'),
        ('tiered', 'Escalonado por monto'),
    ]

    # ── Commission rates ──
    standard_commission_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=Decimal('0.2000'),
        help_text='Comisión para talentos Standard (ej: 0.20 = 20%)'
    )
    premium_commission_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=Decimal('0.1500'),
        help_text='Comisión para talentos Premium (ej: 0.15 = 15%)'
    )
    partner_commission_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=Decimal('0.3000'),
        help_text='Comisión del partner sobre la comisión de la plataforma (ej: 0.30 = 30%)'
    )

    # ── Service fee ("Gestión y garantía") ──
    service_fee_name = models.CharField(
        max_length=100, default='Gestión y garantía',
        help_text='Nombre del fee que se muestra al cliente'
    )
    service_fee_mode = models.CharField(
        max_length=10, choices=SERVICE_FEE_MODE_CHOICES, default='percentage',
        help_text='Modo de cálculo del fee: porcentaje o escalonado'
    )
    service_fee_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=Decimal('0.0500'),
        help_text='Fee como porcentaje del total (ej: 0.05 = 5%)'
    )
    # Tiered fee amounts
    service_fee_small = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal('15.00'),
        help_text='Fee para eventos pequeños ($150–$400)'
    )
    service_fee_medium = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal('20.00'),
        help_text='Fee para eventos medianos ($400–$800)'
    )
    service_fee_large = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal('25.00'),
        help_text='Fee para eventos grandes ($800+)'
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'platform_config'
        verbose_name = 'Configuración de Plataforma'
        verbose_name_plural = 'Configuración de Plataforma'

    def save(self, *args, **kwargs):
        # Ensure only one instance exists (singleton)
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_config(cls):
        """Get or create the singleton config."""
        config, _ = cls.objects.get_or_create(pk=1)
        return config

    def __str__(self):
        return (
            f"Standard: {self.standard_commission_rate*100}% | "
            f"Premium: {self.premium_commission_rate*100}% | "
            f"Partner: {self.partner_commission_rate*100}%"
        )
