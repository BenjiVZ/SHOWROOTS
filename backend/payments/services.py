"""
Servicios de negocio del módulo de pagos.
Aislados de las vistas para facilitar testing y reuso (desde webhook + desde confirm).
"""
from decimal import Decimal
import logging

from django.utils import timezone

from bookings.models import Booking, BookingPack, Payment, PlatformConfig

from .models import PaguelofacilTransaction, Payout

logger = logging.getLogger(__name__)


def create_payment_and_payouts(tx: PaguelofacilTransaction) -> Payment:
    """
    Llamada cuando una PaguelofacilTransaction pasa a 'approved'.

    1. Crea un Payment en el booking (que dispara calculate_commissions).
    2. Genera los Payout pendientes para cada proveedor:
       - El DJ del booking (siempre).
       - Cada Aliado dueño de un Pack en el booking (si hay).
    3. Dispara emails de confirmación (cliente, DJ, aliados).

    Idempotente: si ya hay payment_id en la tx, no hace nada.
    """
    if tx.payment_id:
        return tx.payment

    booking: Booking = tx.booking

    payment = Payment.objects.create(
        booking=booking,
        client=tx.client,
        amount=tx.amount,
        payment_type=tx.payment_type,
        payment_status='completed',
        payment_method='card',
        transaction_ref=f'PFL:{tx.paguelofacil_id or tx.internal_reference}',
        notes=(
            f'Aprobado vía Paguelofacil '
            f'(authStatus {tx.paguelofacil_auth_code or "—"})'
        ),
    )
    tx.payment = payment
    tx.approved_at = timezone.now()

    _create_payouts_for_payment(booking, payment)

    # Emails de notificación — best-effort, no bloquean si fallan
    from .emails import notify_payment_approved
    try:
        notify_payment_approved(tx)
    except Exception:
        logger.exception('Fallo enviando emails de confirmación de pago')

    return payment


def _create_payouts_for_payment(booking: Booking, payment: Payment) -> None:
    """
    Genera los Payouts pendientes proporcionalmente al monto del payment.

    Reglas:
      - DJ recibe su share calculado por Payment.calculate_commissions (`talent_payout`)
        proporcional a la fracción dj_base / total_base.
      - Cada Aliado recibe (línea pack / total_base) * amount, menos pack_commission_rate.
      - Si hay varios packs del mismo Aliado, se agrupan en un solo Payout.
      - Si Aliado y DJ coinciden (caso raro), se generan dos Payouts separados igual,
        para que el admin pueda procesarlos por separado en su transferencia.
    """
    config = PlatformConfig.get_config()
    pack_rate = config.pack_commission_rate

    dj_base = booking.final_price or Decimal('0.00')
    packs_base = booking.packs_subtotal or Decimal('0.00')
    total_base = dj_base + packs_base

    # ── Payout al DJ ──
    # Reutilizamos el talent_payout que calculate_commissions ya dejó en el Payment.
    # En reservas de solo-servicios (sin DJ) no hay talento: se omite este payout y
    # el dinero se reparte solo entre los Aliados de los packs (abajo).
    if booking.talent and payment.talent_payout > 0:
        Payout.objects.create(
            booking=booking,
            recipient=booking.talent.user,
            recipient_kind='talent',
            amount=payment.talent_payout,
            status='pending',
            notes='Pago automático generado al aprobarse el cobro PFL.',
        )

    # ── Payouts para Aliados ──
    if total_base <= 0 or packs_base <= 0:
        return

    booking_packs = list(
        BookingPack.objects.select_related('pack__partner__user')
        .filter(booking=booking)
    )
    if not booking_packs:
        return

    # Agrupar por partner.user (ya que un partner puede tener varios packs en la misma reserva)
    by_partner: dict[int, dict] = {}
    for bp in booking_packs:
        partner_user = bp.pack.partner.user
        line_total = Decimal(str(bp.price_at_booking)) * bp.quantity
        bucket = by_partner.setdefault(
            partner_user.id,
            {'user': partner_user, 'gross': Decimal('0.00'), 'packs': []},
        )
        bucket['gross'] += line_total
        bucket['packs'].append(f'{bp.pack.name} x{bp.quantity}')

    for data in by_partner.values():
        partner_share_of_payment = (
            Decimal(str(payment.amount)) * data['gross'] / total_base
        ).quantize(Decimal('0.01'))
        commission = (partner_share_of_payment * pack_rate).quantize(Decimal('0.01'))
        net = partner_share_of_payment - commission
        if net <= 0:
            continue
        Payout.objects.create(
            booking=booking,
            recipient=data['user'],
            recipient_kind='partner',
            amount=net,
            status='pending',
            notes=(
                f'Packs: {", ".join(data["packs"])} | '
                f'Bruto pack-share: ${partner_share_of_payment} | '
                f'Comisión Pulsar ({pack_rate*100:.0f}%): ${commission}'
            ),
        )


def process_refund(tx: PaguelofacilTransaction, amount: Decimal, reason: str = '') -> dict:
    """
    Procesa un reembolso parcial o total a través de la API de PFL.

    Actualiza la tx local y el Payment asociado.
    Si el reembolso es total, cancela los Payouts pendientes asociados.
    """
    from .paguelofacil import refund as pfl_refund, PaguelofacilAPIError

    if tx.status == 'refunded':
        raise ValueError('La transacción ya fue reembolsada por completo.')
    if tx.status != 'approved':
        raise ValueError('Solo se pueden reembolsar transacciones aprobadas.')
    if not tx.paguelofacil_id:
        raise ValueError('Falta el codOper de PFL — no se puede reembolsar.')
    if amount <= 0:
        raise ValueError('El monto del reembolso debe ser mayor a 0.')

    # I5: tope acumulado. La suma de todos los reembolsos no puede superar lo cobrado.
    already = tx.refunded_amount or Decimal('0.00')
    if already + amount > tx.amount + Decimal('0.01'):
        disponible = tx.amount - already
        raise ValueError(
            f'El reembolso (${amount}) excede el saldo reembolsable (${disponible}). '
            f'Ya reembolsado ${already} de ${tx.amount}.'
        )

    api_response = pfl_refund(tx.paguelofacil_id, amount)
    tx.webhook_payloads = (tx.webhook_payloads or []) + [
        {'event': 'refund', 'amount': str(amount), 'response': api_response}
    ]
    tx.refunded_amount = already + amount

    is_full_refund = tx.refunded_amount >= tx.amount
    if is_full_refund:
        tx.status = 'refunded'
        if tx.payment:
            tx.payment.payment_status = 'refunded'
            tx.payment.notes = (tx.payment.notes or '') + f'\n[Reembolso total: {reason}]'
            tx.payment.save(update_fields=['payment_status', 'notes'])
        # Cancelar payouts pendientes (los ya pagados quedan como están y hay que recuperar manualmente)
        Payout.objects.filter(
            booking=tx.booking,
            status='pending',
        ).update(status='cancelled', notes='Cancelado por reembolso total.')
    else:
        tx.payment.notes = (tx.payment.notes or '') + f'\n[Reembolso parcial ${amount}: {reason}]'
        tx.payment.save(update_fields=['notes'])

    tx.save()
    return api_response
