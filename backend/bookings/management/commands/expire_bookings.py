"""
Management command to expire old booking requests.
Run periodically via cron/task scheduler:
  python manage.py expire_bookings
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from bookings.models import Booking, Notification


class Command(BaseCommand):
    help = 'Expire unresponded booking requests after their expiration time (default 48h)'

    def handle(self, *args, **options):
        now = timezone.now()
        expired = Booking.objects.filter(
            status='solicitud_enviada',
            expires_at__lte=now
        )
        count = expired.count()

        for booking in expired:
            booking.status = 'cancelada'
            booking.save(update_fields=['status', 'updated_at'])

            # Notify the client
            Notification.objects.create(
                user=booking.client,
                notification_type='system',
                title='Solicitud expirada',
                message=f'Tu solicitud para {booking.talent.stage_name} del {booking.event_date} ha expirado sin respuesta.',
                link=f'/dashboard/bookings/{booking.id}'
            )

            # Notify the talent
            Notification.objects.create(
                user=booking.talent.user,
                notification_type='system',
                title='Solicitud expirada',
                message=f'La solicitud de {booking.client.get_full_name()} para el {booking.event_date} ha expirado.',
                link=f'/dashboard/bookings/{booking.id}'
            )

        self.stdout.write(
            self.style.SUCCESS(f'Expiradas {count} solicitudes pendientes.')
        )
