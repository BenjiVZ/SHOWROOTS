"""
Middleware para actualizar `last_seen_at` del usuario autenticado.
Se usa para decidir cuándo enviar notificaciones por email (no notificar
si el usuario está activo en la plataforma).
"""
from datetime import timedelta
from django.utils import timezone


class LastSeenMiddleware:
    """Actualiza User.last_seen_at en cada request autenticada (throttled a 60s)."""

    THROTTLE_SECONDS = 60

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            user = getattr(request, 'user', None)
            if user and user.is_authenticated:
                now = timezone.now()
                last = user.last_seen_at
                if (not last) or (now - last) > timedelta(seconds=self.THROTTLE_SECONDS):
                    # update_fields evita disparar señales/auto_now de otros campos
                    type(user).objects.filter(pk=user.pk).update(last_seen_at=now)
        except Exception:
            # Nunca rompas el response por un fallo de tracking
            pass
        return response
