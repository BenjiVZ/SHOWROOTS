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
        ('en_disputa', 'En Disputa'),
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
    # Panamá ITBMS (7%)
    tax_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00'),
        help_text='ITBMS 7% calculado sobre el total'
    )

    # Public booking code (ej: PUL-2026-05-A8F3)
    booking_code = models.CharField(
        max_length=24, blank=True, unique=True, db_index=True,
        help_text='Código público corto para mostrar al cliente'
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
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'

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

    def calculate_tax(self, rate=Decimal('0.07')):
        """Calculate Panama ITBMS (7%) over the service_fee base."""
        base = self.service_fee or Decimal('0.00')
        self.tax_amount = (base * rate).quantize(Decimal('0.01'))
        return self.tax_amount

    @property
    def total_to_pay(self):
        """Total que el cliente paga: DJ + packs + service fee + ITBMS."""
        base = self.quoted_price or self.precio_estimado or Decimal('0.00')
        return (
            base
            + self.packs_subtotal
            + (self.service_fee or Decimal('0.00'))
            + (self.tax_amount or Decimal('0.00'))
        ).quantize(Decimal('0.01'))

    def cancellation_refund(self, when=None):
        """
        Compute refund amount if cancelled at `when` (default now).
        Returns dict with refund_amount, refund_rate, window_label.
        """
        from datetime import datetime
        from django.utils import timezone as _tz
        config = PlatformConfig.get_config()
        when = when or _tz.now()
        # Días al evento
        event_dt = datetime.combine(self.event_date, self.event_time_start)
        if _tz.is_aware(when) and _tz.is_naive(event_dt):
            event_dt = _tz.make_aware(event_dt)
        days_to_event = (event_dt - when).days
        paid = Decimal(str(self.amount_paid or 0))

        if days_to_event >= config.cancel_full_refund_days:
            rate = Decimal('1.00')
            label = f'Más de {config.cancel_full_refund_days} días — reembolso 100%'
        elif days_to_event >= config.cancel_partial_refund_days:
            rate = config.cancel_partial_refund_rate
            label = f'Entre {config.cancel_partial_refund_days} y {config.cancel_full_refund_days} días — reembolso {int(rate*100)}%'
        else:
            rate = Decimal('0.00')
            label = f'Menos de {config.cancel_partial_refund_days} días — sin reembolso'

        return {
            'days_to_event': days_to_event,
            'refund_rate': str(rate),
            'refund_amount': str((paid * rate).quantize(Decimal('0.01'))),
            'window_label': label,
            'paid': str(paid),
        }

    def is_high_season(self):
        """Check si el evento cae en alta temporada (mes en high_season_months)."""
        config = PlatformConfig.get_config()
        months = config.high_season_months or []
        if not self.event_date or not months:
            return False
        return self.event_date.month in months

    def calculate_dynamic_surcharge(self):
        """Sobreprecio Premium en alta temporada (sólo si talent_level == 'premium')."""
        if self.talent.talent_level != 'premium':
            return Decimal('0.00')
        if not self.is_high_season():
            return Decimal('0.00')
        config = PlatformConfig.get_config()
        base = self.quoted_price or self.precio_estimado or Decimal('0.00')
        return (base * config.high_season_surcharge_rate).quantize(Decimal('0.01'))

    @staticmethod
    def generate_booking_code():
        """Generate code like PUL-2026-05-A8F3."""
        import secrets, string
        from datetime import datetime
        now = datetime.now()
        rand = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
        return f"PUL-{now.year}-{now.month:02d}-{rand}"

    def save(self, *args, **kwargs):
        if not self.booking_code:
            # Try up to 5 times in case of collision
            for _ in range(5):
                code = self.generate_booking_code()
                if not Booking.objects.filter(booking_code=code).exists():
                    self.booking_code = code
                    break
        super().save(*args, **kwargs)

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
    def packs_subtotal(self):
        """Suma de todos los production packs agregados al booking."""
        total = Decimal('0.00')
        for bp in self.production_packs.all():
            total += (Decimal(str(bp.price_at_booking)) * bp.quantity)
        return total.quantize(Decimal('0.01'))

    @property
    def total_client_cost(self):
        """Total que paga el cliente = DJ + packs + service fee."""
        price = self.final_price or Decimal('0.00')
        return (price + self.packs_subtotal + (self.service_fee or Decimal('0.00'))).quantize(Decimal('0.01'))

    @property
    def remaining_balance(self):
        """Amount still owed (incluye packs + service fee)."""
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
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'

    def __str__(self):
        return f"Payment ${self.amount} - Booking #{self.booking_id} ({self.get_payment_status_display()})"

    def calculate_commissions(self, platform_rate=None, partner_rate=None):
        """
        Calculate commission breakdown — separa la porción DJ y la porción Packs.
        - DJ portion: rate por tier (Standard 22% / Pro 15% / Premium 12%)
        - Packs portion: pack_commission_rate (default 20%)
        - Partner referrer: 30% de la comisión total (sobre ambas porciones)

        El monto del payment se atribuye proporcionalmente entre DJ y packs según
        el peso de cada uno en el booking total.
        """
        from bookings.models import PlatformConfig
        config = PlatformConfig.get_config()

        # Determine platform commission based on talent level
        if platform_rate is None:
            talent_level = self.booking.talent.talent_level
            if talent_level == 'premium':
                platform_rate = config.premium_commission_rate
            elif talent_level == 'pro':
                platform_rate = config.pro_commission_rate
            else:
                platform_rate = config.standard_commission_rate

        if partner_rate is None:
            partner_rate = config.partner_commission_rate

        pack_rate = config.pack_commission_rate

        # Split this payment proporcionalmente entre la base DJ y la base packs
        dj_base = self.booking.final_price or Decimal('0.00')
        packs_base = self.booking.packs_subtotal
        total_base = dj_base + packs_base

        if total_base > 0:
            dj_share = (Decimal(str(self.amount)) * dj_base / total_base).quantize(Decimal('0.01'))
            pack_share = (Decimal(str(self.amount)) - dj_share).quantize(Decimal('0.01'))
        else:
            dj_share = Decimal(str(self.amount))
            pack_share = Decimal('0.00')

        commission_dj = (dj_share * platform_rate).quantize(Decimal('0.01'))
        commission_packs = (pack_share * pack_rate).quantize(Decimal('0.01'))

        self.commission_showroots = commission_dj + commission_packs
        if self.booking.partner:
            self.commission_partner = (self.commission_showroots * partner_rate).quantize(Decimal('0.01'))
            self.commission_showroots -= self.commission_partner
        # `talent_payout` aquí representa "lo que va al proveedor" — DJ + Aliados de Packs comparten esto
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
    raw_content = models.TextField(
        blank=True, help_text='Texto original antes del scanner anti-desintermediación'
    )
    flagged = models.BooleanField(
        default=False, help_text='True si el scanner anti-disinter detectó intento de contacto fuera de plataforma'
    )
    flagged_categories = models.JSONField(
        default=list, blank=True,
        help_text='Categorías detectadas (phone, email, whatsapp, etc.)'
    )
    file_url = models.URLField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'messages'
        ordering = ['created_at']
        verbose_name = 'Mensaje'
        verbose_name_plural = 'Mensajes'

    def save(self, *args, **kwargs):
        # Run anti-disintermediation scanner on the content
        if self.content and not self.pk:
            from .anti_disinter import sanitize
            clean, findings = sanitize(self.content)
            if findings:
                self.raw_content = self.content
                self.content = clean
                self.flagged = True
                self.flagged_categories = list({cat for cat, _ in findings})
        super().save(*args, **kwargs)

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
        ('tier_upgrade', 'Subida de Tier'),
        ('premium_invitation', 'Invitación Premium'),
        ('flagged_warning', 'Advertencia de Mensaje'),
        # Solicitudes abiertas ("Uber para DJs")
        ('open_gig_available', 'Solicitud Abierta Disponible'),
        ('open_gig_offer_received', 'Nueva Oferta Recibida'),
        ('open_gig_offer_accepted', 'Oferta Aceptada'),
        ('open_gig_offer_rejected', 'Oferta Rechazada'),
        ('open_gig_expired', 'Solicitud Expirada'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=32, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=300, blank=True, help_text='URL interna')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'

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
    # Dimension scores (1-5) — opcionales para mantener compatibilidad con reseñas viejas
    rating_punctuality = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Puntualidad'
    )
    rating_music_selection = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Selección musical'
    )
    rating_crowd_reading = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Lectura del público'
    )
    rating_technique = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Técnica'
    )
    rating_communication = models.PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Comunicación pre-evento'
    )
    comment = models.TextField()
    # Respuesta pública del talento (sólo Premium puede responder según business rule).
    response = models.TextField(
        blank=True, help_text='Respuesta pública del talento a la reseña (sólo Premium)'
    )
    response_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reviews'
        ordering = ['-created_at']
        verbose_name = 'Reseña'
        verbose_name_plural = 'Reseñas'

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

    # ── Commission rates por tier ──
    standard_commission_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=Decimal('0.2000'),
        help_text='Comisión Standard (ej: 0.20 = 20%)'
    )
    pro_commission_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=Decimal('0.1500'),
        help_text='Comisión Pro (ej: 0.15 = 15%)'
    )
    premium_commission_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=Decimal('0.1200'),
        help_text='Comisión Premium (ej: 0.12 = 12%)'
    )
    partner_commission_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=Decimal('0.3000'),
        help_text='Comisión del partner sobre la comisión de la plataforma (ej: 0.30 = 30%)'
    )
    pack_commission_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=Decimal('0.2000'),
        help_text='Comisión Pulsar sobre packs de producción (ej: 0.20 = 20%)'
    )

    # ── Auto-promoción Standard → Pro ──
    auto_promote_min_events = models.PositiveIntegerField(
        default=10, help_text='Eventos mínimos completados para promoción auto a Pro'
    )
    auto_promote_min_rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=Decimal('4.50'),
        help_text='Rating promedio mínimo para promoción a Pro'
    )

    # ── Cancellation policy windows (días antes del evento) ──
    cancel_full_refund_days = models.PositiveIntegerField(
        default=7, help_text='Días antes del evento con reembolso 100%'
    )
    cancel_partial_refund_days = models.PositiveIntegerField(
        default=2, help_text='Días antes del evento con reembolso 50%'
    )
    cancel_partial_refund_rate = models.DecimalField(
        max_digits=4, decimal_places=2, default=Decimal('0.50'),
        help_text='Porcentaje de reembolso en el rango parcial (ej: 0.50 = 50%)'
    )

    # ── Pricing dinámico Premium ──
    high_season_months = models.JSONField(
        default=list, blank=True,
        help_text='Meses de alta temporada (1-12). Ej: [11, 12, 1] = nov-dic-ene'
    )
    high_season_surcharge_rate = models.DecimalField(
        max_digits=4, decimal_places=2, default=Decimal('0.15'),
        help_text='Sobreprecio en alta temporada para Premium (ej: 0.15 = +15%)'
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


class ClientCredit(models.Model):
    """Crédito Pulsar acumulado por un cliente (ej: $50 al dejar una reseña)."""

    REASON_CHOICES = [
        ('review_reward', 'Recompensa por dejar reseña'),
        ('referral', 'Referencia'),
        ('refund', 'Reembolso'),
        ('promo', 'Promoción'),
        ('manual', 'Ajuste manual'),
    ]

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='credits'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES, default='manual')
    booking = models.ForeignKey(
        Booking, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='credits_generated'
    )
    used = models.BooleanField(default=False, help_text='Si el crédito ya fue redimido')
    used_on = models.ForeignKey(
        Booking, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='credits_redeemed'
    )
    note = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'client_credits'
        ordering = ['-created_at']
        verbose_name = 'Crédito de cliente'
        verbose_name_plural = 'Créditos de cliente'

    def __str__(self):
        return f"${self.amount} · {self.client} · {self.get_reason_display()}"


class PremiumInvitation(models.Model):
    """Invitación de Pulsar a un talento para subir a Premium. No es automática."""

    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('accepted', 'Aceptada'),
        ('declined', 'Rechazada'),
        ('expired', 'Expirada'),
        ('revoked', 'Revocada'),
    ]

    talent = models.ForeignKey(
        'talents.TalentProfile',
        on_delete=models.CASCADE,
        related_name='premium_invitations'
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='premium_invitations_sent',
        help_text='Admin que envió la invitación'
    )
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(
        blank=True,
        help_text='Mensaje opcional al talento explicando la invitación'
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'premium_invitations'
        ordering = ['-sent_at']
        verbose_name = 'Invitación a Premium'
        verbose_name_plural = 'Invitaciones a Premium'

    def __str__(self):
        return f"{self.talent.stage_name} · {self.get_status_display()}"

    def accept(self):
        from django.utils import timezone as _tz
        self.status = 'accepted'
        self.responded_at = _tz.now()
        self.talent.talent_level = 'premium'
        self.talent.save(update_fields=['talent_level', 'updated_at'])
        self.save()
        # Notify
        Notification.objects.create(
            user=self.talent.user,
            notification_type='tier_upgrade',
            title='¡Eres Premium!',
            message='Has aceptado la invitación a Pulsar Premium. Ya estás en el tier más alto.',
            link='/talent-dashboard'
        )

    def decline(self):
        from django.utils import timezone as _tz
        self.status = 'declined'
        self.responded_at = _tz.now()
        self.save()


class Dispute(models.Model):
    """Reporte de problema en un booking. Retiene el pago al talento hasta resolución."""

    REASON_CHOICES = [
        ('no_show', 'No se presentó'),
        ('late', 'Llegó muy tarde'),
        ('poor_service', 'Servicio deficiente'),
        ('different_artist', 'Vino un artista distinto'),
        ('equipment_failure', 'Fallas con el equipo'),
        ('other', 'Otro'),
    ]

    STATUS_CHOICES = [
        ('open', 'Abierta'),
        ('investigating', 'En revisión'),
        ('resolved_refund', 'Resuelta — reembolso'),
        ('resolved_paid', 'Resuelta — pago al talento'),
        ('resolved_split', 'Resuelta — repartido'),
        ('closed', 'Cerrada sin acción'),
    ]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='dispute')
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='disputes_reported'
    )
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    admin_notes = models.TextField(blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='disputes_resolved'
    )
    refund_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text='Monto reembolsado al cliente'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'disputes'
        ordering = ['-created_at']
        verbose_name = 'Disputa'
        verbose_name_plural = 'Disputas'

    def __str__(self):
        return f"Disputa booking #{self.booking_id} · {self.get_status_display()}"


class AuditLog(models.Model):
    """Trail de acciones administrativas. Quién hizo qué y cuándo."""

    ACTION_CHOICES = [
        ('talent_approve', 'Aprobar talento'),
        ('talent_reject', 'Rechazar talento'),
        ('booking_refund', 'Emitir reembolso'),
        ('dispute_resolve', 'Resolver disputa'),
        ('premium_invite', 'Invitar a Premium'),
        ('user_ban', 'Banear usuario'),
        ('user_warn', 'Advertir usuario (flagged)'),
        ('config_change', 'Cambiar config plataforma'),
        ('other', 'Otra'),
    ]

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='audit_actions'
    )
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    target_type = models.CharField(max_length=50, blank=True, help_text='Tipo del objeto afectado (booking, talent, user, etc.)')
    target_id = models.PositiveIntegerField(null=True, blank=True)
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']
        verbose_name = 'Registro de auditoría'
        verbose_name_plural = 'Registros de auditoría'

    def __str__(self):
        return f"{self.actor} · {self.get_action_display()} · {self.created_at:%Y-%m-%d %H:%M}"


# ── Partner de Producción (renta de equipo) ──

class PartnerProductionProfile(models.Model):
    """
    Perfil de producción de un Aliado: categorías de equipo, cobertura, verificación.
    Necesario antes de publicar packs (sección 2 del mockup).
    """

    CATEGORY_CHOICES = [
        ('sound', 'Sonido'),
        ('lights', 'Iluminación'),
        ('screens', 'Pantallas'),
        ('mics', 'Microfonía'),
        ('dj_booth', 'DJ Booth'),
        ('fx', 'FX / Especiales'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('pending', 'Pendiente de verificación'),
        ('verified', 'Verificado'),
        ('rejected', 'Rechazado'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='production_profile'
    )
    categories = models.JSONField(
        default=list, blank=True,
        help_text='Lista de categorías ofrecidas (slugs). Ej: ["sound", "lights", "mics"]'
    )
    main_city = models.CharField(max_length=100, blank=True)
    coverage_radius_km = models.PositiveIntegerField(
        default=50, help_text='Radio de cobertura en km'
    )
    travel_fee_extra = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        help_text='Cargo extra fuera del radio de cobertura'
    )
    max_simultaneous_events = models.PositiveIntegerField(
        default=1, help_text='Máximo de eventos simultáneos (por noche)'
    )
    notes = models.TextField(blank=True, help_text='Notas adicionales del partner')

    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='draft')
    submitted_at = models.DateTimeField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='production_profiles_verified'
    )
    rejection_reason = models.TextField(blank=True)
    onboarding_step = models.PositiveSmallIntegerField(
        default=1, help_text='Paso actual del wizard (1-4). 4 = completado y enviado a verificación.'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'partner_production_profiles'
        ordering = ['-created_at']
        verbose_name = 'Perfil de producción (Aliado)'
        verbose_name_plural = 'Perfiles de producción (Aliados)'

    def __str__(self):
        return f"{self.user.username} · Production · {self.get_status_display()}"

    @property
    def photo_count(self):
        return self.photos.count()

    def submit_for_verification(self):
        """Marca el perfil como pendiente de verificación humana."""
        from django.utils import timezone as _tz
        self.status = 'pending'
        self.submitted_at = _tz.now()
        self.onboarding_step = 4
        self.save(update_fields=['status', 'submitted_at', 'onboarding_step', 'updated_at'])


class PartnerProductionPhoto(models.Model):
    """Foto de equipo del Partner. Mínimo 4 para verificación."""

    profile = models.ForeignKey(
        PartnerProductionProfile,
        on_delete=models.CASCADE,
        related_name='photos'
    )
    file = models.ImageField(upload_to='partner/equipment/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'partner_production_photos'
        ordering = ['order', 'uploaded_at']
        verbose_name = 'Foto de equipo (Aliado)'
        verbose_name_plural = 'Fotos de equipo (Aliados)'

    def __str__(self):
        return f"Photo #{self.id} · {self.profile.user.username}"


class ProductionPack(models.Model):
    """
    Pack de producción que un Partner publica. El cliente lo agrega al booking.
    Ej: "Pack Sonido Pro · 80-300 personas · $500".
    """

    EVENT_SIZE_CHOICES = [
        ('small',  'Pequeño (<80)'),
        ('medium', 'Mediano (80-300)'),
        ('large',  'Grande (300+)'),
    ]

    STATUS_CHOICES = [
        ('draft',     'Borrador'),
        ('published', 'Publicado'),
        ('paused',    'Pausado'),
    ]

    partner = models.ForeignKey(
        PartnerProductionProfile,
        on_delete=models.CASCADE,
        related_name='packs'
    )
    name = models.CharField(max_length=150)
    category = models.CharField(
        max_length=20,
        choices=PartnerProductionProfile.CATEGORY_CHOICES,
        help_text='Categoría de equipo: sound, lights, screens, mics, dj_booth, fx'
    )
    short_description = models.CharField(max_length=200, blank=True)
    event_size = models.CharField(
        max_length=10, choices=EVENT_SIZE_CHOICES, default='medium'
    )
    equipment_items = models.JSONField(
        default=list, blank=True,
        help_text='Items incluidos. Ej: ["2x QSC KW153", "Mixer Pioneer DJM-A9", ...]'
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    includes_technician = models.BooleanField(default=True)
    includes_setup = models.BooleanField(default=True)
    includes_dj = models.BooleanField(
        default=False,
        help_text='Si el pack incluye DJ — turnkey: el cliente reserva sólo este pack y no necesita buscar DJ aparte.'
    )
    dj_name = models.CharField(
        max_length=120, blank=True,
        help_text='Nombre del DJ que viene con el pack (opcional). Si el aliado es DJ + equipo, normalmente es él mismo.'
    )
    setup_hours_before = models.PositiveSmallIntegerField(default=2)
    available_days = models.JSONField(
        default=list, blank=True,
        help_text='Días disponibles. Ej: ["mon","tue","wed","thu","fri","sat"]'
    )
    cover_image = models.ImageField(upload_to='partner/packs/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    rentals_count = models.PositiveIntegerField(default=0)
    rating_avg = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'production_packs'
        ordering = ['-rentals_count', '-created_at']
        verbose_name = 'Pack de producción'
        verbose_name_plural = 'Packs de producción'

    def __str__(self):
        return f"{self.name} · ${self.price} · {self.partner.user.username}"

    @property
    def is_visible_publicly(self):
        """Solo publicado y el partner verificado puede aparecer en el catálogo."""
        return self.status == 'published' and self.partner.status == 'verified'


class BookingPack(models.Model):
    """
    Pack agregado a un booking. Snapshot del precio al momento del agregado
    (el precio del pack puede cambiar después y no debe afectar bookings históricos).
    """

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='production_packs'
    )
    pack = models.ForeignKey(
        ProductionPack,
        on_delete=models.PROTECT,
        related_name='booking_uses'
    )
    price_at_booking = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'booking_packs'
        ordering = ['created_at']
        unique_together = ['booking', 'pack']
        verbose_name = 'Pack en reserva'
        verbose_name_plural = 'Packs en reservas'

    def __str__(self):
        return f"Booking #{self.booking_id} · {self.pack.name} (${self.price_at_booking})"

    @property
    def line_total(self):
        from decimal import Decimal
        return (Decimal(str(self.price_at_booking)) * self.quantity).quantize(Decimal('0.01'))


class PackBundle(models.Model):
    """
    Combo de varios ProductionPacks con descuento. Ej: "Sonido Pro + Luces Show -15%".
    El cliente lo agrega como una unidad y se le aplican todos los packs.
    """

    partner = models.ForeignKey(
        PartnerProductionProfile,
        on_delete=models.CASCADE,
        related_name='bundles'
    )
    name = models.CharField(max_length=150)
    description = models.CharField(max_length=300, blank=True)
    packs = models.ManyToManyField(ProductionPack, related_name='bundles')
    discount_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('10.00'),
        help_text='Descuento sobre la suma de precios individuales (ej: 15.00 = 15%)'
    )
    status = models.CharField(
        max_length=10,
        choices=[('draft', 'Borrador'), ('published', 'Publicado'), ('paused', 'Pausado')],
        default='draft',
    )
    rentals_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pack_bundles'
        ordering = ['-rentals_count', '-created_at']
        verbose_name = 'Combo de packs'
        verbose_name_plural = 'Combos de packs'

    def __str__(self):
        return f"Bundle: {self.name} ({self.discount_percentage}% off)"

    @property
    def base_price(self):
        """Suma de precios individuales de los packs (antes de descuento)."""
        total = Decimal('0.00')
        for p in self.packs.all():
            total += Decimal(str(p.price))
        return total.quantize(Decimal('0.01'))

    @property
    def discounted_price(self):
        """Precio final con descuento aplicado."""
        return (self.base_price * (Decimal('100') - self.discount_percentage) / Decimal('100')).quantize(Decimal('0.01'))


# ─────────────────────────────────────────────────────────────────────────────
# Solicitudes abiertas ("Uber para DJs")
# ─────────────────────────────────────────────────────────────────────────────

class OpenGigRequest(models.Model):
    """
    Solicitud abierta publicada por un cliente. Los DJs elegibles reciben la
    notificación de forma escalonada por tier (Premium → Pro → Standard).
    Cuando el cliente acepta una oferta, se crea un Booking normal y esta
    request queda en estado 'assigned'.
    """

    STATUS_CHOICES = [
        ('open', 'Abierta'),
        ('assigned', 'Asignada'),
        ('expired', 'Expirada'),
        ('cancelled', 'Cancelada'),
    ]

    VISIBLE_TIER_CHOICES = [
        ('premium', 'Solo Premium'),
        ('pro', 'Premium + Pro'),
        ('all', 'Todos'),
    ]

    # Catálogo cerrado de "qué necesito"
    REQUESTED_ITEM_CHOICES = [
        ('dj',      'DJ'),
        ('sound',   'Sonido'),
        ('lights',  'Luces'),
        ('booth',   'DJ Booth'),
        ('screens', 'Pantallas'),
        ('other',   'Otro'),
    ]
    PACK_ITEMS = {'sound', 'lights', 'booth', 'screens', 'other'}

    # Autor
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='open_gig_requests'
    )

    # Qué necesita el cliente (lista de slugs de REQUESTED_ITEM_CHOICES)
    requested_items = models.JSONField(
        default=list, blank=True,
        help_text='Lista de items solicitados: dj, sound, lights, booth, screens, other'
    )

    # Detalles del evento (espejo de Booking)
    event_type = models.CharField(max_length=20, choices=Booking.EVENT_TYPE_CHOICES)
    event_name = models.CharField(max_length=200, blank=True)
    event_date = models.DateField()
    event_time_start = models.TimeField()
    event_time_end = models.TimeField()
    event_duration_hours = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    event_location = models.CharField(max_length=300)
    event_city = models.CharField(max_length=100, blank=True)
    event_indoor = models.BooleanField(default=True)
    guest_count = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    genre_preference = models.CharField(max_length=100, blank=True)

    # Servicios adicionales (mismo shape que Booking)
    additional_services = models.JSONField(default=list, blank=True)
    additional_services_notes = models.TextField(blank=True)

    # Presupuesto (opcional, referencia para los DJs)
    budget = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    # Escalonamiento
    visible_to_tier = models.CharField(
        max_length=10, choices=VISIBLE_TIER_CHOICES, default='premium',
        help_text='Hasta qué tier ven la solicitud actualmente'
    )
    notify_pro_at = models.DateTimeField(
        null=True, blank=True,
        help_text='Momento en que se debe notificar a los Pro'
    )
    notify_standard_at = models.DateTimeField(
        null=True, blank=True,
        help_text='Momento en que se debe notificar a los Standard'
    )
    pro_notified_at = models.DateTimeField(null=True, blank=True)
    standard_notified_at = models.DateTimeField(null=True, blank=True)

    # Ciclo de vida
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='open')
    expires_at = models.DateTimeField(
        null=True, blank=True,
        help_text='Expiración automática si no se acepta oferta'
    )
    assigned_booking = models.ForeignKey(
        Booking, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='open_gig_source',
        help_text='Booking creado cuando se aceptó una oferta'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'open_gig_requests'
        ordering = ['-created_at']
        verbose_name = 'Solicitud abierta'
        verbose_name_plural = 'Solicitudes abiertas'
        indexes = [
            models.Index(fields=['status', 'visible_to_tier']),
            models.Index(fields=['status', 'expires_at']),
        ]

    def __str__(self):
        return f"OpenGig #{self.id} — {self.client} ({self.get_status_display()})"

    @property
    def is_expired(self):
        if self.status == 'open' and self.expires_at:
            return timezone.now() > self.expires_at
        return False

    def tier_visible(self, tier: str) -> bool:
        """¿Un talento con este tier puede ver la solicitud ahora?"""
        if self.status != 'open':
            return False
        if self.visible_to_tier == 'premium':
            return tier == 'premium'
        if self.visible_to_tier == 'pro':
            return tier in ('premium', 'pro')
        return True  # 'all'

    @property
    def needs_dj(self) -> bool:
        return 'dj' in (self.requested_items or [])

    @property
    def needs_packs(self) -> bool:
        return bool(self.PACK_ITEMS & set(self.requested_items or []))

    @property
    def requested_items_display(self) -> list:
        """Etiquetas legibles para UI: [{'key': 'dj', 'label': 'DJ'}, ...]"""
        m = dict(self.REQUESTED_ITEM_CHOICES)
        return [{'key': k, 'label': m.get(k, k)} for k in (self.requested_items or [])]


class GigOffer(models.Model):
    """
    Oferta sobre una OpenGigRequest.

    Puede venir de:
      - Un DJ (talent seteado, offer_kind='dj')
      - Un Aliado de producción (partner seteado, offer_kind='pack', puede incluir pack FK)
    """

    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('accepted', 'Aceptada'),
        ('rejected', 'Rechazada'),
        ('withdrawn', 'Retirada'),
    ]

    KIND_CHOICES = [
        ('dj',   'DJ'),
        ('pack', 'Pack de producción'),
    ]

    request = models.ForeignKey(
        OpenGigRequest, on_delete=models.CASCADE, related_name='offers'
    )
    offer_kind = models.CharField(max_length=6, choices=KIND_CHOICES, default='dj')

    # Uno de los dos debe estar seteado
    talent = models.ForeignKey(
        'talents.TalentProfile', on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='gig_offers'
    )
    partner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='partner_gig_offers',
        help_text='Usuario Aliado que oferta un pack'
    )
    pack = models.ForeignKey(
        ProductionPack, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='+',
        help_text='Pack ofrecido por el aliado (opcional)'
    )
    # Qué categoría de item cubre la oferta (para ofertas 'pack').
    # Debe ser uno de OpenGigRequest.REQUESTED_ITEM_CHOICES (sound/lights/booth/screens/other).
    covers_item = models.CharField(max_length=10, blank=True, default='')

    quoted_price = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True, help_text='Mensaje para el cliente')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'gig_offers'
        ordering = ['-created_at']
        verbose_name = 'Oferta'
        verbose_name_plural = 'Ofertas'
        constraints = [
            models.UniqueConstraint(
                fields=['request', 'talent'], name='unique_offer_per_talent',
                condition=models.Q(talent__isnull=False),
            ),
        ]

    def __str__(self):
        provider = self.talent or self.partner
        return f"Oferta #{self.id} ({self.offer_kind}) — {provider} → OpenGig #{self.request_id}"
