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


def send_welcome_email(user):
    """Envía email de bienvenida al registrarse. Mensaje según rol."""
    name = user.first_name or user.username
    if user.role == 'talent':
        subject = '¡Bienvenido a Pulsar! Próximos pasos'
        intro = 'Te diste de alta como <strong>Talento</strong>. Estás a un paso de empezar a recibir reservas.'
        steps = (
            'Completa tu perfil con foto de portada, géneros y tarifas.'
            '|Sube tus mejores fotos y un video corto.'
            '|Pulsar revisará tu perfil y te aprobará para aparecer en búsqueda.'
        )
        cta_text = 'Completar mi perfil'
        cta_url = f"{settings.FRONTEND_URL}/talent-dashboard"
    elif user.role == 'partner':
        subject = '¡Bienvenido a Pulsar como Aliado!'
        intro = 'Te diste de alta como <strong>Aliado</strong>. Ya puedes empezar a gestionar reservas para tus clientes.'
        steps = (
            'Explora el catálogo de talentos.'
            '|Reserva en nombre de tus clientes.'
            '|Cobra tu comisión automática por cada reserva confirmada.'
        )
        cta_text = 'Ir al panel'
        cta_url = f"{settings.FRONTEND_URL}/partner-dashboard"
    else:
        subject = '¡Bienvenido a Pulsar!'
        intro = 'Gracias por registrarte. En Pulsar reservas DJs y talentos con pago en custodia — tu dinero queda protegido hasta que el evento se realice.'
        steps = (
            'Busca el talento ideal según género, fecha y presupuesto.'
            '|Envía una solicitud sin compromiso.'
            '|El talento te responde en máximo 48h con su propuesta.'
        )
        cta_text = 'Buscar talentos'
        cta_url = f"{settings.FRONTEND_URL}/search"

    steps_html = ''.join(
        f'<li style="margin-bottom:8px;">{s}</li>' for s in steps.split('|')
    )

    text = (
        f'Hola {name},\n\n'
        f'Bienvenido a Pulsar. Visita {cta_url} para continuar.\n\n'
        f'— Equipo Pulsar by ShowRoots'
    )

    html = f"""
    <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0d0d0d; color: #e0e0e0; border-radius: 16px; overflow: hidden;">
      <div style="background: linear-gradient(135deg, #c1d82f, #a9bf26); padding: 32px; text-align: center;">
        <h1 style="margin: 0; font-size: 24px; color: #0d0d0d; font-weight: 800;">PULSAR</h1>
        <p style="margin: 4px 0 0; font-size: 11px; color: #333; letter-spacing: 2px; text-transform: uppercase;">by ShowRoots</p>
      </div>
      <div style="padding: 32px;">
        <h2 style="color: #c1d82f; margin-top: 0;">¡Bienvenido, {name}!</h2>
        <p style="line-height:1.6;">{intro}</p>
        <h3 style="color:#c1d82f; font-size:15px; margin-top:24px;">Próximos pasos</h3>
        <ol style="color:#ccc; line-height:1.5; padding-left:20px;">{steps_html}</ol>
        <div style="text-align: center; margin: 32px 0 8px;">
          <a href="{cta_url}" style="display: inline-block; padding: 14px 32px; background: #c1d82f; color: #0d0d0d; text-decoration: none; border-radius: 8px; font-weight: 700; font-size: 15px;">
            {cta_text}
          </a>
        </div>
      </div>
      <div style="padding: 16px 32px; background: #111; text-align: center; font-size: 12px; color: #666;">
        © Pulsar by ShowRoots — Marketplace de Talentos Musicales
      </div>
    </div>
    """

    send_pulsar_email(subject, text, [user.email], html_message=html)


def send_new_message_email(recipient, sender, booking, preview):
    """Email cuando llega un mensaje en el chat de un booking."""
    sender_name = sender.get_full_name() or sender.username
    rcpt_name = recipient.first_name or recipient.username
    booking_url = f"{settings.FRONTEND_URL}/dashboard/bookings/{booking.id}"
    preview = (preview or '').strip()
    if len(preview) > 140:
        preview = preview[:140] + '…'

    subject = f'Nuevo mensaje de {sender_name}'
    text = (
        f'Hola {rcpt_name},\n\n'
        f'{sender_name} te envió un mensaje sobre la reserva {booking.booking_code or "#" + str(booking.id)}:\n\n'
        f'"{preview}"\n\n'
        f'Responde desde Pulsar: {booking_url}\n\n'
        f'— Equipo Pulsar by ShowRoots'
    )

    html = f"""
    <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #0d0d0d; color: #e0e0e0; border-radius: 16px; overflow: hidden;">
      <div style="background: linear-gradient(135deg, #c1d82f, #a9bf26); padding: 24px 32px;">
        <h1 style="margin: 0; font-size: 20px; color: #0d0d0d; font-weight: 800;">PULSAR</h1>
        <p style="margin: 4px 0 0; font-size: 10px; color: #333; letter-spacing: 2px; text-transform: uppercase;">by ShowRoots</p>
      </div>
      <div style="padding: 32px;">
        <h2 style="color: #c1d82f; margin-top: 0; font-size:18px;">💬 Nuevo mensaje de {sender_name}</h2>
        <p>Hola <strong>{rcpt_name}</strong>, te escribieron en la reserva <code style="color:#c1d82f;">{booking.booking_code or '#' + str(booking.id)}</code>.</p>
        <blockquote style="margin: 16px 0; padding: 14px 18px; background:#1a1a1a; border-left:3px solid #c1d82f; border-radius:6px; color:#e0e0e0; font-style: italic;">
          {preview}
        </blockquote>
        <p style="color:#888; font-size:13px;">Por seguridad, respóndele dentro de Pulsar — no compartas teléfono ni redes en el chat.</p>
        <div style="text-align: center; margin: 24px 0;">
          <a href="{booking_url}" style="display: inline-block; padding: 12px 28px; background: #c1d82f; color: #0d0d0d; text-decoration: none; border-radius: 8px; font-weight: 700;">
            Responder en Pulsar
          </a>
        </div>
      </div>
      <div style="padding: 16px 32px; background: #111; text-align: center; font-size: 12px; color: #666;">
        © Pulsar by ShowRoots — Marketplace de Talentos Musicales
      </div>
    </div>
    """

    send_pulsar_email(subject, text, [recipient.email], html_message=html)


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
