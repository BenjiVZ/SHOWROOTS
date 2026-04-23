"""
Pulsar by ShowRoots — Email notifications utility.

In dev mode (console backend), emails are printed to the terminal.
In production, set environment variables for SMTP delivery.
"""

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


def send_pulsar_email(subject, message_text, recipient_list, html_message=None):
    """Send a branded email. Falls back to text if no HTML."""
    send_mail(
        subject=f'Pulsar - {subject}',
        message=message_text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list if isinstance(recipient_list, list) else [recipient_list],
        html_message=html_message,
        fail_silently=True,
    )


# Keep legacy alias for backward compatibility
send_showroots_email = send_pulsar_email


def send_password_reset_email(user, uid, token):
    """Send password reset link to user."""
    reset_url = f"{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}"

    subject = 'Restablecer tu contraseña'
    message = (
        f'Hola {user.first_name or user.username},\n\n'
        f'Recibimos una solicitud para restablecer tu contraseña en Pulsar.\n'
        f'Haz clic en el siguiente enlace para crear una nueva contraseña:\n\n'
        f'{reset_url}\n\n'
        f'Este enlace expira en 24 horas.\n'
        f'Si no solicitaste este cambio, ignora este correo.\n\n'
        f'— Equipo Pulsar by ShowRoots'
    )

    html = f"""
    <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0d0d0d; color: #e0e0e0; border-radius: 16px; overflow: hidden;">
      <div style="background: linear-gradient(135deg, #c1d82f, #a9bf26); padding: 32px; text-align: center;">
        <h1 style="margin: 0; font-size: 24px; color: #0d0d0d; font-weight: 800;">PULSAR</h1>
        <p style="margin: 4px 0 0; font-size: 11px; color: #333; letter-spacing: 2px; text-transform: uppercase;">by ShowRoots</p>
      </div>
      <div style="padding: 32px;">
        <h2 style="color: #c1d82f; margin-top: 0;">Restablecer Contraseña</h2>
        <p>Hola <strong>{user.first_name or user.username}</strong>,</p>
        <p>Recibimos una solicitud para restablecer tu contraseña en Pulsar.</p>
        <div style="text-align: center; margin: 32px 0;">
          <a href="{reset_url}" style="display: inline-block; padding: 14px 32px; background: #c1d82f; color: #0d0d0d; text-decoration: none; border-radius: 8px; font-weight: 700; font-size: 16px;">
            Restablecer Contraseña
          </a>
        </div>
        <p style="color: #888; font-size: 14px;">Este enlace expira en 24 horas. Si no solicitaste este cambio, ignora este correo.</p>
      </div>
      <div style="padding: 16px 32px; background: #111; text-align: center; font-size: 12px; color: #666;">
        © Pulsar by ShowRoots — Marketplace de Talentos Musicales
      </div>
    </div>
    """

    send_pulsar_email(subject, message, [user.email], html_message=html)


def send_booking_notification_email(user, subject, body_text, booking=None):
    """Send a booking-related notification email."""
    booking_url = f"{settings.FRONTEND_URL}/dashboard/bookings/{booking.id}" if booking else ""

    html = f"""
    <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0d0d0d; color: #e0e0e0; border-radius: 16px; overflow: hidden;">
      <div style="background: linear-gradient(135deg, #c1d82f, #a9bf26); padding: 24px 32px;">
        <h1 style="margin: 0; font-size: 20px; color: #0d0d0d; font-weight: 800;">PULSAR</h1>
        <p style="margin: 4px 0 0; font-size: 10px; color: #333; letter-spacing: 2px; text-transform: uppercase;">by ShowRoots</p>
      </div>
      <div style="padding: 32px;">
        <h2 style="color: #c1d82f; margin-top: 0;">{subject}</h2>
        <p>Hola <strong>{user.first_name or user.username}</strong>,</p>
        <p>{body_text}</p>
        {'<div style="text-align: center; margin: 24px 0;"><a href="' + booking_url + '" style="display: inline-block; padding: 12px 28px; background: #c1d82f; color: #0d0d0d; text-decoration: none; border-radius: 8px; font-weight: 700;">Ver Reserva</a></div>' if booking_url else ''}
      </div>
      <div style="padding: 16px 32px; background: #111; text-align: center; font-size: 12px; color: #666;">
        © Pulsar by ShowRoots — Marketplace de Talentos Musicales
      </div>
    </div>
    """

    send_pulsar_email(subject, body_text, [user.email], html_message=html)
