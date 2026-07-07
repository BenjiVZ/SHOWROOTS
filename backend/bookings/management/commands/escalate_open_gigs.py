"""
Escala la visibilidad de las solicitudes abiertas (OpenGigRequest).

Este command corre el ciclo de "fan-out" tipo Uber:
  - Cuando llega `notify_pro_at`   → abre visibilidad a Pro    → notifica Pro.
  - Cuando llega `notify_standard_at` → abre visibilidad a todos → notifica Standard.
  - Cuando llega `expires_at` sin oferta aceptada → marca la request como 'expired'.

Se puede correr manualmente (`python manage.py escalate_open_gigs`) o
disparar por APScheduler (`bookings.management.commands.run_scheduler`).
"""
import logging
from django.core.management.base import BaseCommand
from django.utils import timezone

logger = logging.getLogger('pulsar.scheduler')


def escalate_open_gigs_job():
    """Promueve tier + envía notificaciones para OpenGigRequest pendientes."""
    from bookings.models import OpenGigRequest, Notification
    from bookings.views import _notify_talents_for_open_gig

    now = timezone.now()
    promoted_pro = 0
    promoted_std = 0
    expired = 0

    # 1) Promover a Pro (solo requests que piden DJ)
    to_pro = OpenGigRequest.objects.filter(
        status='open',
        visible_to_tier='premium',
        notify_pro_at__lte=now,
    )
    for gig in to_pro:
        if not gig.needs_dj:
            # Requests solo-de-packs no tienen staging por tier
            continue
        gig.visible_to_tier = 'pro'
        gig.pro_notified_at = now
        gig.save(update_fields=['visible_to_tier', 'pro_notified_at', 'updated_at'])
        _notify_talents_for_open_gig(gig, tier='pro')
        promoted_pro += 1

    # 2) Promover a Standard (todos)
    to_std = OpenGigRequest.objects.filter(
        status='open',
        visible_to_tier__in=['premium', 'pro'],
        notify_standard_at__lte=now,
    )
    for gig in to_std:
        if not gig.needs_dj:
            continue
        gig.visible_to_tier = 'all'
        gig.standard_notified_at = now
        gig.save(update_fields=['visible_to_tier', 'standard_notified_at', 'updated_at'])
        _notify_talents_for_open_gig(gig, tier='standard')
        promoted_std += 1

    # 3) Expirar solicitudes sin oferta aceptada
    to_expire = OpenGigRequest.objects.filter(
        status='open', expires_at__lte=now,
    )
    for gig in to_expire:
        gig.status = 'expired'
        gig.save(update_fields=['status', 'updated_at'])
        gig.offers.filter(status='pending').update(status='rejected')
        Notification.objects.create(
            user=gig.client,
            notification_type='open_gig_expired',
            title='Tu solicitud expiró',
            message=(
                f'Tu solicitud abierta para el {gig.event_date} expiró sin ofertas aceptadas. '
                f'Podés publicarla de nuevo o buscar un DJ directamente.'
            ),
            link=f'/dashboard/open-gigs/{gig.id}',
        )
        expired += 1

    if promoted_pro or promoted_std or expired:
        logger.info(
            f'[escalate_open_gigs] pro={promoted_pro} standard={promoted_std} expired={expired}'
        )
    else:
        logger.debug('[escalate_open_gigs] nada que hacer')

    return {'promoted_pro': promoted_pro, 'promoted_std': promoted_std, 'expired': expired}


class Command(BaseCommand):
    help = 'Promueve la visibilidad tier-a-tier de las solicitudes abiertas y expira las vencidas.'

    def handle(self, *args, **options):
        result = escalate_open_gigs_job()
        self.stdout.write(self.style.SUCCESS(
            f'OK — pro={result["promoted_pro"]} '
            f'standard={result["promoted_std"]} expired={result["expired"]}'
        ))
