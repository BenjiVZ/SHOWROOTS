"""Notificaciones (in-app + email) para el flujo de pagos manuales.

Se usa desde las vistas (al crear la orden) y desde el backoffice (al aprobar o
rechazar). Todo es best-effort: si el email falla, no rompe la operación.
"""
import logging

from django.conf import settings
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)


def _frontend():
    return getattr(settings, 'FRONTEND_URL', '').rstrip('/')


def _send(subject, text, recipients):
    from accounts.emails import send_pulsar_email
    recipients = [r for r in recipients if r]
    if not recipients:
        return
    try:
        send_pulsar_email(subject, text, recipients)
    except Exception:
        logger.exception('Fallo enviando email de pago manual')


def _notify(user, ntype, title, message, link=''):
    from .models import Notification
    try:
        Notification.objects.create(
            user=user, notification_type=ntype, title=title, message=message, link=link,
        )
    except Exception:
        logger.exception('Fallo creando notificación de pago manual')


def notify_staff_new_manual_payment(order):
    """Avisa a los admins que entró una orden manual por revisar."""
    User = get_user_model()
    staff = list(User.objects.filter(is_staff=True, is_active=True))
    link = '/admin/bookings/manualpaymentorder/'
    booking_ref = order.booking.booking_code or order.booking_id
    who = order.client.get_full_name() or order.client.username
    for u in staff:
        _notify(
            u, 'payment_received', 'Nuevo pago manual por revisar',
            f'{who} declaró un pago de ${order.amount} ({order.method.name}) '
            f'para la reserva {booking_ref}. Ref: {order.reference}.',
            link,
        )
    _send(
        'Nuevo pago manual por revisar en Pulsar',
        f'{who} declaró un pago de ${order.amount} vía {order.method.name} '
        f'(ref {order.reference}) para la reserva {booking_ref}. '
        f'Válidalo en el backoffice: {_frontend()}{link}',
        [u.email for u in staff],
    )


def notify_client_manual_payment_approved(order):
    """Avisa al cliente que su pago fue validado y la reserva quedó confirmada.
    También notifica in-app al DJ y a los Aliados de packs de la reserva."""
    link = f'/dashboard/bookings/{order.booking_id}'
    _notify(
        order.client, 'booking_confirmed', '¡Pago confirmado!',
        f'Validamos tu pago de ${order.amount} ({order.method.name}). '
        f'Tu reserva quedó confirmada.',
        link,
    )
    _send(
        'Tu pago fue confirmado — Pulsar',
        f'¡Listo! Confirmamos tu pago de ${order.amount} vía {order.method.name}. '
        f'Tu reserva está confirmada. Verla: {_frontend()}{link}',
        [order.client.email],
    )
    # DJ + Aliados de la reserva
    try:
        notify_providers_payment_received(order.booking)
    except Exception:
        logger.exception('Fallo notificando a proveedores tras pago manual')


def notify_client_payment_confirmed(booking):
    """In-app al cliente: pago confirmado + reserva confirmada (usado por la ruta PFL)."""
    _notify(
        booking.client, 'booking_confirmed', '¡Pago confirmado!',
        f'Tu pago fue confirmado y la reserva del {booking.event_date} quedó confirmada.',
        f'/dashboard/bookings/{booking.id}',
    )


def notify_providers_payment_received(booking):
    """In-app al DJ y a los Aliados con packs en la reserva cuando entra el cobro.
    Solo in-app — el email de confirmación lo maneja cada flujo por separado."""
    from .models import BookingPack
    date = booking.event_date
    link = f'/dashboard/bookings/{booking.id}'
    if booking.talent:
        _notify(
            booking.talent.user, 'payment_received', '¡Cobro recibido!',
            f'Se confirmó el pago de la reserva del {date}. Tu liquidación se procesará.',
            link,
        )
    seen = set()
    for bp in BookingPack.objects.select_related('pack__partner__user').filter(booking=booking):
        u = bp.pack.partner.user
        if u.id in seen:
            continue
        seen.add(u.id)
        _notify(
            u, 'payment_received', '¡Cobro recibido!',
            f'Tu pack en la reserva del {date} fue pagado. Tu liquidación se procesará.',
            link,
        )


def notify_client_manual_payment_rejected(order):
    """Avisa al cliente que no se pudo validar el pago (con motivo)."""
    link = f'/dashboard/bookings/{order.booking_id}'
    reason = order.rejection_reason or 'No pudimos validar el comprobante.'
    _notify(
        order.client, 'system', 'Pago no validado',
        f'No pudimos validar tu pago de ${order.amount} ({order.method.name}). '
        f'Motivo: {reason} Podés reintentar el pago.',
        link,
    )
    _send(
        'No pudimos validar tu pago — Pulsar',
        f'No pudimos validar tu pago de ${order.amount} vía {order.method.name}. '
        f'Motivo: {reason} Podés volver a intentarlo: {_frontend()}{link}',
        [order.client.email],
    )
