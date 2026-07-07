"""
Pulsar — Background Task Scheduler.

Runs periodic tasks using APScheduler (Windows-compatible, no Redis needed).

Usage:
    python manage.py run_scheduler

Tasks:
    - expire_bookings: Cancels unresponded bookings after 48h (runs every hour)
    - send_reminders: Sends event reminders 24h before (runs every 6 hours)
"""

import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger('pulsar.scheduler')


def expire_bookings_job():
    """Cancel bookings that haven't been responded to in 48 hours."""
    from bookings.models import Booking, Notification

    now = timezone.now()
    expired = Booking.objects.filter(
        status__in=['solicitud_enviada', 'pendiente_respuesta'],
        expires_at__lte=now
    )

    count = 0
    for booking in expired:
        booking.status = 'cancelada'
        booking.save(update_fields=['status'])

        # Notify client
        Notification.objects.create(
            user=booking.client,
            notification_type='booking_expired',
            title='Solicitud expirada',
            message=f'Tu solicitud para {booking.talent.stage_name} expiró por falta de respuesta.',
            link=f'/dashboard/bookings/{booking.id}'
        )

        # Notify talent
        Notification.objects.create(
            user=booking.talent.user,
            notification_type='booking_expired',
            title='Solicitud expirada',
            message=f'La solicitud de {booking.client.get_full_name()} expiró sin respuesta.',
            link=f'/dashboard/bookings/{booking.id}'
        )

        # Send email notifications
        try:
            from accounts.emails import send_booking_notification_email
            send_booking_notification_email(
                booking.client,
                'Solicitud Expirada',
                f'Tu solicitud para {booking.talent.stage_name} del {booking.event_date} expiró porque no fue respondida a tiempo. Puedes buscar otro talento.',
                booking=booking
            )
        except Exception:
            pass

        count += 1

    if count > 0:
        logger.info(f'[expire_bookings] {count} reserva(s) expirada(s)')
    else:
        logger.debug('[expire_bookings] No hay reservas expiradas')


def send_reminders_job():
    """Send reminders for events happening within the next 24 hours."""
    from bookings.models import Booking, Notification
    from datetime import timedelta

    tomorrow = timezone.now().date() + timedelta(days=1)

    upcoming = Booking.objects.filter(
        status='confirmada',
        event_date=tomorrow
    ).select_related('client', 'talent', 'talent__user')

    count = 0
    for booking in upcoming:
        # Remind client
        Notification.objects.create(
            user=booking.client,
            notification_type='event_reminder',
            title='¡Tu evento es mañana!',
            message=f'Recuerda: {booking.talent.stage_name} estará en tu evento mañana ({booking.event_date}).',
            link=f'/dashboard/bookings/{booking.id}'
        )

        # Remind talent
        Notification.objects.create(
            user=booking.talent.user,
            notification_type='event_reminder',
            title='Tienes un evento mañana',
            message=f'Recuerda: tienes un evento para {booking.client.get_full_name()} mañana ({booking.event_date}).',
            link=f'/dashboard/bookings/{booking.id}'
        )

        # Send emails
        try:
            from accounts.emails import send_booking_notification_email
            send_booking_notification_email(
                booking.client,
                '¡Tu evento es mañana!',
                f'{booking.talent.stage_name} estará en tu evento mañana. ¡Prepárate!',
                booking=booking
            )
            send_booking_notification_email(
                booking.talent.user,
                'Tienes un evento mañana',
                f'Recuerda que tienes un evento para {booking.client.get_full_name()} mañana.',
                booking=booking
            )
        except Exception:
            pass

        count += 1

    if count > 0:
        logger.info(f'[send_reminders] {count} recordatorio(s) enviado(s)')


def auto_complete_bookings_job():
    """Auto-mark confirmed bookings as completed after the event date passes."""
    from bookings.models import Booking, Notification

    today = timezone.now().date()
    past_events = Booking.objects.filter(
        status='confirmada',
        event_date__lt=today
    ).select_related('client', 'talent', 'talent__user')

    count = 0
    for booking in past_events:
        booking.status = 'completada'
        booking.save(update_fields=['status', 'updated_at'])

        # Update talent stats
        talent = booking.talent
        talent.total_bookings = Booking.objects.filter(
            talent=talent, status='completada'
        ).count()
        talent.save(update_fields=['total_bookings'])

        # Notify client to leave a review
        Notification.objects.create(
            user=booking.client,
            notification_type='booking_completed',
            title='Evento completado',
            message=f'Tu evento con {booking.talent.stage_name} ha sido completado. ¡Deja una reseña!',
            link=f'/dashboard/bookings/{booking.id}'
        )
        Notification.objects.create(
            user=booking.talent.user,
            notification_type='booking_completed',
            title='Evento completado',
            message=f'El evento para {booking.client.get_full_name()} ha finalizado.',
            link=f'/dashboard/bookings/{booking.id}'
        )

        try:
            from accounts.emails import send_booking_notification_email
            send_booking_notification_email(
                booking.client,
                'Evento Completado — ¡Deja tu reseña!',
                f'Tu evento con {booking.talent.stage_name} ha sido marcado como completado. ¡Nos encantaría saber tu opinión!',
                booking=booking
            )
        except Exception:
            pass

        count += 1

    if count > 0:
        logger.info(f'[auto_complete] {count} evento(s) completado(s) automáticamente')
    else:
        logger.debug('[auto_complete] No hay eventos para completar')


class Command(BaseCommand):
    help = 'Inicia el scheduler de tareas periódicas de Pulsar'

    def handle(self, *args, **options):
        from bookings.management.commands.escalate_open_gigs import escalate_open_gigs_job

        scheduler = BlockingScheduler()

        # Expirar reservas sin respuesta — cada hora
        scheduler.add_job(
            expire_bookings_job,
            trigger=IntervalTrigger(hours=1),
            id='expire_bookings',
            name='Expirar reservas sin respuesta (48h)',
            replace_existing=True,
        )

        # Recordatorios de eventos — cada 6 horas
        scheduler.add_job(
            send_reminders_job,
            trigger=IntervalTrigger(hours=6),
            id='send_reminders',
            name='Recordatorios de eventos proximos (24h antes)',
            replace_existing=True,
        )

        # Auto-completar eventos pasados — cada 12 horas
        scheduler.add_job(
            auto_complete_bookings_job,
            trigger=IntervalTrigger(hours=12),
            id='auto_complete_bookings',
            name='Auto-completar eventos pasados',
            replace_existing=True,
        )

        # Escalation de solicitudes abiertas ("Uber para DJs") — cada minuto
        scheduler.add_job(
            escalate_open_gigs_job,
            trigger=IntervalTrigger(minutes=1),
            id='escalate_open_gigs',
            name='Escalar visibilidad de solicitudes abiertas por tier',
            replace_existing=True,
        )

        self.stdout.write(self.style.SUCCESS(
            '\n'
            '============================================\n'
            '   Pulsar Task Scheduler                    \n'
            '============================================\n'
            '   expire_bookings    -> cada 1 hora        \n'
            '   send_reminders     -> cada 6 horas       \n'
            '   auto_complete      -> cada 12 horas      \n'
            '   escalate_open_gigs -> cada 1 minuto      \n'
            '============================================\n'
        ))
        self.stdout.write('Scheduler ejecutandose... (Ctrl+C para detener)\n')

        # Run initial jobs immediately on startup
        self.stdout.write('Ejecutando tareas iniciales...')
        expire_bookings_job()
        send_reminders_job()
        auto_complete_bookings_job()
        escalate_open_gigs_job()
        self.stdout.write(self.style.SUCCESS('Tareas iniciales completadas\n'))

        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            self.stdout.write(self.style.WARNING('\nScheduler detenido.'))
