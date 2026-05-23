"""
Señales de auto-promoción de tier.

Cuando un talento completa N eventos con rating promedio ≥ X,
se promueve automáticamente de Standard → Pro. Premium NO es automático
(siempre por invitación de Pulsar).
"""
from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Review, Notification, PlatformConfig


def _talent_event_count(talent):
    """Eventos completados del talento (excluye cancelaciones)."""
    return talent.bookings.filter(status='completada').count()


def _talent_recent_cancellations(talent, months=6):
    """Cancelaciones del talento en los últimos N meses."""
    from datetime import timedelta
    from django.utils import timezone as _tz
    cutoff = _tz.now() - timedelta(days=months * 30)
    return talent.bookings.filter(
        status='cancelada',
        updated_at__gte=cutoff,
    ).count()


def check_and_promote_to_pro(talent):
    """
    Promueve a 'pro' si:
      - talent_level actual es 'standard'
      - eventos completados ≥ config.auto_promote_min_events
      - rating_avg ≥ config.auto_promote_min_rating
      - 0 cancelaciones en los últimos 6 meses
    """
    if talent.talent_level != 'standard':
        return False

    config = PlatformConfig.get_config()
    event_count = _talent_event_count(talent)
    if event_count < config.auto_promote_min_events:
        return False

    rating = Decimal(str(talent.rating_avg or 0))
    if rating < config.auto_promote_min_rating:
        return False

    if _talent_recent_cancellations(talent, months=6) > 0:
        return False

    # Promote!
    talent.talent_level = 'pro'
    talent.save(update_fields=['talent_level', 'updated_at'])
    Notification.objects.create(
        user=talent.user,
        notification_type='tier_upgrade',
        title='¡Subiste a Pulsar Pro!',
        message=(
            f'Completaste {event_count} eventos con rating {rating}★ y cero cancelaciones. '
            f'Tu comisión bajó al 15%. ¡Felicidades!'
        ),
        link='/talent-dashboard'
    )
    return True


@receiver(post_save, sender=Review)
def review_post_save(sender, instance, created, **kwargs):
    """Cuando llega una reseña nueva, revisar si el talento entra en Pro."""
    if not created:
        return
    try:
        check_and_promote_to_pro(instance.talent)
    except Exception:
        # No queremos romper el flujo de reviews si la promoción falla
        pass
