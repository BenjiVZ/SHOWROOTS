"""
Modelos para integración con pasarelas de pago.
Por ahora: Paguelofacil (CCLW + S2S webhook).
"""
from decimal import Decimal
from django.conf import settings
from django.db import models

from bookings.models import Booking, Payment


class PaguelofacilTransaction(models.Model):
    """
    Registro de cada intento de cobro vía Paguelofacil.

    Una Booking puede tener varias PaguelofacilTransaction (reintentos, abono+saldo, etc.).
    Cuando el webhook confirma una, se crea/actualiza un Payment del modelo del Booking.
    """

    STATUS_CHOICES = [
        ('initiated', 'Iniciada'),         # generamos URL, esperando que el user pague
        ('processing', 'Procesando'),      # PFL devolvió pending
        ('approved', 'Aprobada'),          # PFL confirmó pago
        ('declined', 'Rechazada'),         # tarjeta rechazada
        ('cancelled', 'Cancelada'),        # user canceló o expiró
        ('refunded', 'Reembolsada'),
        ('error', 'Error'),
    ]

    PAYMENT_TYPE_CHOICES = [
        ('deposit', 'Abono/Depósito'),
        ('full', 'Pago Total'),
        ('balance', 'Saldo Restante'),
    ]

    # Referencias internas
    booking = models.ForeignKey(
        Booking, on_delete=models.PROTECT,
        related_name='paguelofacil_transactions'
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='paguelofacil_transactions'
    )
    payment = models.OneToOneField(
        Payment, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='paguelofacil_tx',
        help_text='El Payment del booking creado al aprobarse esta transacción.'
    )

    # Atributos del cobro
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPE_CHOICES, default='full')
    description = models.CharField(max_length=200, blank=True)
    # Monto reembolsado acumulado (para topar reembolsos parciales — vuln I5)
    refunded_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00'),
        help_text='Suma de todos los reembolsos ya procesados sobre esta transacción.'
    )

    # Estado
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='initiated')

    # Identificadores Paguelofacil
    # CTRL/Reference: lo generamos nosotros — único por transacción, lo enviamos a PFL
    internal_reference = models.CharField(max_length=64, unique=True, db_index=True)
    # ID/OperationId que devuelve PFL una vez procesado
    paguelofacil_id = models.CharField(max_length=120, blank=True, db_index=True)
    paguelofacil_auth_code = models.CharField(max_length=64, blank=True)

    # Auditoría completa de la conversación con PFL
    request_payload = models.JSONField(default=dict, blank=True)
    response_payload = models.JSONField(default=dict, blank=True)
    webhook_payloads = models.JSONField(default=list, blank=True)
    last_error = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'paguelofacil_transactions'
        ordering = ['-created_at']
        verbose_name = 'Transacción Paguelofacil'
        verbose_name_plural = 'Transacciones Paguelofacil'
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['booking', 'status']),
        ]

    def __str__(self):
        return f"PFL {self.internal_reference} · {self.amount} {self.currency} · {self.get_status_display()}"

    @property
    def is_final(self):
        """¿Llegó a un estado terminal?"""
        return self.status in ('approved', 'declined', 'cancelled', 'refunded', 'error')


class Payout(models.Model):
    """
    Registro del pago manual a un proveedor (DJ o Aliado) por una booking ya cobrada.

    Pulsar cobra todo via Paguelofacil. Después, fuera del sistema (transferencia bancaria,
    Yappy, ACH), el equipo le manda al DJ/Aliado su parte. Acá se asienta ese pago.
    """

    PAYOUT_STATUS = [
        ('pending', 'Pendiente'),
        ('processing', 'En proceso'),
        ('paid', 'Pagado'),
        ('on_hold', 'En espera'),
        ('cancelled', 'Cancelado'),
    ]

    PAYOUT_METHOD = [
        ('bank_transfer', 'Transferencia bancaria'),
        ('yappy', 'Yappy'),
        ('cash', 'Efectivo'),
        ('other', 'Otro'),
    ]

    RECIPIENT_KIND = [
        ('talent', 'DJ / Talento'),
        ('partner', 'Aliado de Producción'),
    ]

    booking = models.ForeignKey(
        Booking, on_delete=models.PROTECT, related_name='payouts'
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='payouts_received'
    )
    recipient_kind = models.CharField(max_length=10, choices=RECIPIENT_KIND)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')

    status = models.CharField(max_length=12, choices=PAYOUT_STATUS, default='pending')
    method = models.CharField(max_length=15, choices=PAYOUT_METHOD, blank=True)
    reference = models.CharField(
        max_length=120, blank=True,
        help_text='Número de transferencia / referencia bancaria del pago'
    )
    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='payouts_created',
        help_text='Admin que registró el pago'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'payouts'
        ordering = ['-created_at']
        verbose_name = 'Payout'
        verbose_name_plural = 'Payouts (a DJs/Aliados)'

    def __str__(self):
        return f"Payout {self.amount} {self.currency} → {self.recipient.email} ({self.get_status_display()})"
