"""
Notificaciones por email del módulo de pagos.

Envíos:
  - Cliente: recibo de pago aprobado.
  - DJ / Talento: aviso de cobro confirmado.
  - Aliados de packs: aviso de cobro de su porción.
  - Admin (al equipo Pulsar): heads-up de nuevo Payout pendiente.

Reutilizan accounts.emails.send_pulsar_email para mantener branding consistente.
"""
from decimal import Decimal
import logging

from django.conf import settings

from accounts.emails import send_pulsar_email
from bookings.models import Payment

from .models import PaguelofacilTransaction, Payout

logger = logging.getLogger(__name__)


def _money(v) -> str:
    try:
        return f'${Decimal(str(v)):.2f}'
    except Exception:
        return f'${v}'


def _booking_url(booking_id: int) -> str:
    base = (getattr(settings, 'FRONTEND_URL', '') or '').rstrip('/')
    return f'{base}/dashboard/bookings/{booking_id}'


def send_payment_confirmed_to_client(tx: PaguelofacilTransaction) -> None:
    """Email al cliente con el recibo del pago."""
    try:
        booking = tx.booking
        client = tx.client
        if not client.email:
            return
        talent_name = booking.talent.stage_name or booking.talent.user.email
        subject = 'Tu pago fue confirmado'
        text = (
            f'Hola {client.first_name or client.email},\n\n'
            f'Recibimos tu pago de {_money(tx.amount)} USD por la reserva de {talent_name}.\n\n'
            f'Detalles:\n'
            f'  • Reserva: {booking.booking_code or booking.id}\n'
            f'  • Talento: {talent_name}\n'
            f'  • Monto: {_money(tx.amount)} USD\n'
            f'  • Código de operación: {tx.paguelofacil_id or tx.internal_reference}\n\n'
            f'Puedes ver el detalle en: {_booking_url(booking.id)}\n\n'
            f'¡Gracias por usar Pulsar!\n'
        )
        send_pulsar_email(subject, text, [client.email])
    except Exception:
        logger.exception('Fallo enviando email al cliente')


def send_payment_confirmed_to_talent(tx: PaguelofacilTransaction, payment: Payment) -> None:
    """Email al DJ avisándole que el cliente pagó."""
    try:
        booking = tx.booking
        talent_user = booking.talent.user
        if not talent_user.email:
            return
        subject = f'Te pagaron — Reserva {booking.booking_code or booking.id}'
        text = (
            f'Hola {talent_user.first_name or talent_user.email},\n\n'
            f'El cliente confirmó el pago de tu reserva en Pulsar.\n\n'
            f'Detalles:\n'
            f'  • Reserva: {booking.booking_code or booking.id}\n'
            f'  • Cliente: {tx.client.first_name or tx.client.email}\n'
            f'  • Monto cobrado: {_money(tx.amount)} USD\n'
            f'  • Tu parte (después de comisión Pulsar): {_money(payment.talent_payout)} USD\n\n'
            f'Vamos a transferirte tu parte después del evento, conforme a nuestros términos.\n\n'
            f'Ver reserva: {_booking_url(booking.id)}\n'
        )
        send_pulsar_email(subject, text, [talent_user.email])
    except Exception:
        logger.exception('Fallo enviando email al talento')


def send_payment_confirmed_to_partner(partner_payout: Payout) -> None:
    """Email al Aliado dueño de un pack cuando se aprueba el cobro de su porción."""
    try:
        recipient = partner_payout.recipient
        booking = partner_payout.booking
        if not recipient.email:
            return
        subject = f'Te pagaron tu pack — Reserva {booking.booking_code or booking.id}'
        text = (
            f'Hola {recipient.first_name or recipient.email},\n\n'
            f'El cliente confirmó el pago de la reserva donde tu pack está incluido.\n\n'
            f'Detalles:\n'
            f'  • Reserva: {booking.booking_code or booking.id}\n'
            f'  • Tu parte (después de comisión Pulsar): {_money(partner_payout.amount)} USD\n\n'
            f'{partner_payout.notes or ""}\n\n'
            f'Te vamos a transferir tu parte después del evento.\n\n'
            f'Ver reserva: {_booking_url(booking.id)}\n'
        )
        send_pulsar_email(subject, text, [recipient.email])
    except Exception:
        logger.exception('Fallo enviando email al aliado')


def notify_payment_approved(tx: PaguelofacilTransaction) -> None:
    """Punto único de entrada — disparar todos los emails al aprobarse un cobro."""
    if not tx.payment_id:
        return
    payment = tx.payment

    send_payment_confirmed_to_client(tx)
    send_payment_confirmed_to_talent(tx, payment)

    # Avisar a cada Aliado que tenga payout
    partner_payouts = Payout.objects.filter(
        booking=tx.booking,
        recipient_kind='partner',
    )
    for po in partner_payouts:
        send_payment_confirmed_to_partner(po)
