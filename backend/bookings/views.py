from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Booking, Payment, Message, Notification, Review, PlatformConfig
from .models import PremiumInvitation, Dispute, AuditLog
from .serializers import (
    BookingListSerializer, BookingDetailSerializer,
    BookingCreateSerializer, ReviewSerializer,
    PaymentSerializer, PaymentCreateSerializer,
    MessageSerializer, MessageCreateSerializer,
    NotificationSerializer, PartnerStatsSerializer,
    PlatformConfigSerializer, PremiumInvitationSerializer,
    FlaggedMessageSerializer,
)
from django.db.models import Sum, Q, Count
from decimal import Decimal


class IsBookingParticipant(permissions.BasePermission):
    """Only allow the client or talent in the booking to access it."""

    def has_object_permission(self, request, view, obj):
        return (
            obj.client == request.user or
            obj.talent.user == request.user or
            (obj.partner and obj.partner == request.user)
        )


class BookingListView(generics.ListAPIView):
    """List bookings for the authenticated user (as client, talent, or partner)."""
    serializer_class = BookingListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'talent':
            return Booking.objects.filter(talent__user=user)
        elif user.role == 'partner':
            return Booking.objects.filter(partner=user)
        return Booking.objects.filter(client=user)


class BookingCreateView(generics.CreateAPIView):
    """Create a new booking request."""
    serializer_class = BookingCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        booking = serializer.save()
        # Create notification for talent
        Notification.objects.create(
            user=booking.talent.user,
            notification_type='new_request',
            title='Nueva solicitud de reserva',
            message=f'{booking.client.get_full_name()} quiere reservarte para {booking.event_name or booking.get_event_type_display()} el {booking.event_date}.',
            link=f'/dashboard/bookings/{booking.id}'
        )
        # Send email notification
        from accounts.emails import send_booking_notification_email
        send_booking_notification_email(
            booking.talent.user,
            'Nueva Solicitud de Reserva',
            f'{booking.client.get_full_name()} quiere reservarte para {booking.event_name or booking.get_event_type_display()} el {booking.event_date}. Ingresa a tu panel para responder.',
            booking=booking
        )


class BookingDetailView(generics.RetrieveAPIView):
    """Get booking details."""
    queryset = Booking.objects.select_related(
        'client', 'talent', 'talent__user', 'partner'
    ).prefetch_related('payments', 'messages')
    serializer_class = BookingDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsBookingParticipant]


class BookingUpdateStatusView(generics.UpdateAPIView):
    """Update booking status (accept, reject, adjust, complete, cancel)."""
    queryset = Booking.objects.all()
    serializer_class = BookingDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsBookingParticipant]

    def partial_update(self, request, *args, **kwargs):
        booking = self.get_object()
        new_status = request.data.get('status')
        quoted_price = request.data.get('quoted_price')
        talent_notes = request.data.get('talent_notes', '')

        # Valid status transitions
        valid_transitions = {
            'solicitud_enviada': ['pendiente_respuesta', 'aceptada', 'rechazada', 'cancelada'],
            'pendiente_respuesta': ['aceptada', 'rechazada', 'cancelada'],
            'aceptada': ['pendiente_pago', 'cancelada'],
            'pendiente_pago': ['confirmada', 'cancelada'],
            'confirmada': ['completada', 'cancelada'],
        }

        allowed = valid_transitions.get(booking.status, [])
        if new_status not in allowed:
            return Response(
                {'error': f'No se puede cambiar de "{booking.get_status_display()}" a "{new_status}"'},
                status=status.HTTP_400_BAD_REQUEST
            )

        booking.status = new_status
        if quoted_price:
            booking.quoted_price = quoted_price
        if talent_notes:
            booking.talent_notes = talent_notes

        # If talent accepts, move to pending payment
        if new_status == 'aceptada':
            booking.status = 'pendiente_pago'

        booking.save()

        # Auto-block date when confirmed
        if new_status in ('confirmada', 'aceptada'):
            from talents.models import Availability
            Availability.objects.update_or_create(
                talent=booking.talent,
                date=booking.event_date,
                defaults={'status': 'booked', 'note': f'Booking #{booking.id}'}
            )

        # Send notifications
        if new_status in ('aceptada', 'pendiente_pago'):
            Notification.objects.create(
                user=booking.client,
                notification_type='request_accepted',
                title='¡Tu solicitud fue aceptada!',
                message=f'{booking.talent.stage_name} aceptó tu solicitud. Procede al pago para confirmar.',
                link=f'/dashboard/bookings/{booking.id}'
            )
            from accounts.emails import send_booking_notification_email
            send_booking_notification_email(
                booking.client,
                '¡Tu solicitud fue aceptada!',
                f'{booking.talent.stage_name} aceptó tu solicitud para {booking.event_date}. Procede al pago para confirmar la reserva.',
                booking=booking
            )
        elif new_status == 'rechazada':
            Notification.objects.create(
                user=booking.client,
                notification_type='request_rejected',
                title='Solicitud rechazada',
                message=f'{booking.talent.stage_name} no puede asistir a tu evento.',
                link=f'/dashboard/bookings/{booking.id}'
            )
            from accounts.emails import send_booking_notification_email
            send_booking_notification_email(
                booking.client,
                'Solicitud Rechazada',
                f'{booking.talent.stage_name} no puede asistir a tu evento del {booking.event_date}. Puedes buscar otros talentos disponibles.',
                booking=booking
            )
        elif new_status == 'confirmada':
            from accounts.emails import send_booking_notification_email
            for user in [booking.client, booking.talent.user]:
                Notification.objects.create(
                    user=user,
                    notification_type='booking_confirmed',
                    title='¡Reserva confirmada!',
                    message=f'La reserva para {booking.event_date} ha sido confirmada.',
                    link=f'/dashboard/bookings/{booking.id}'
                )
                send_booking_notification_email(
                    user,
                    '¡Reserva Confirmada!',
                    f'La reserva para {booking.event_date} ha sido confirmada. ¡Todo listo!',
                    booking=booking
                )

        # Update talent's total bookings on completion
        if new_status == 'completada':
            talent = booking.talent
            talent.total_bookings = Booking.objects.filter(
                talent=talent, status='completada'
            ).count()
            talent.save(update_fields=['total_bookings'])

            # Notify both parties
            from accounts.emails import send_booking_notification_email
            Notification.objects.create(
                user=booking.client,
                notification_type='booking_completed',
                title='Evento completado',
                message=f'Tu evento con {booking.talent.stage_name} ha sido marcado como completado. ¡Deja una reseña!',
                link=f'/dashboard/bookings/{booking.id}'
            )
            Notification.objects.create(
                user=booking.talent.user,
                notification_type='booking_completed',
                title='Evento completado',
                message=f'El evento para {booking.client.get_full_name()} ha sido completado.',
                link=f'/dashboard/bookings/{booking.id}'
            )
            send_booking_notification_email(
                booking.client,
                'Evento Completado',
                f'Tu evento con {booking.talent.stage_name} ha sido marcado como completado. ¡Nos encantaría saber tu opinión! Deja una reseña.',
                booking=booking
            )

        return Response(BookingDetailSerializer(booking).data)


# ── Payment Views ──

class PaymentCreateView(generics.CreateAPIView):
    """Create a payment for a booking."""
    serializer_class = PaymentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        payment = serializer.save()
        booking = payment.booking
        # Notify both parties
        Notification.objects.create(
            user=booking.talent.user,
            notification_type='payment_received',
            title='¡Pago recibido!',
            message=f'Se recibió un pago de ${payment.amount} para tu evento del {booking.event_date}.',
            link=f'/dashboard/bookings/{booking.id}'
        )
        Notification.objects.create(
            user=booking.client,
            notification_type='booking_confirmed',
            title='Pago procesado',
            message=f'Tu pago de ${payment.amount} fue procesado exitosamente.',
            link=f'/dashboard/bookings/{booking.id}'
        )


class BookingPaymentsView(generics.ListAPIView):
    """List all payments for a booking."""
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(booking_id=self.kwargs['booking_id'])


# ── Message Views ──

class MessageListView(generics.ListAPIView):
    """List messages for a booking."""
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(booking_id=self.kwargs['booking_id'])


class MessageCreateView(generics.CreateAPIView):
    """Send a message in a booking chat."""
    serializer_class = MessageCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        msg = serializer.save()
        # Determine recipient
        booking = msg.booking
        recipient = booking.talent.user if msg.sender == booking.client else booking.client
        Notification.objects.create(
            user=recipient,
            notification_type='new_message',
            title='Nuevo mensaje',
            message=f'{msg.sender.get_full_name()} te envió un mensaje.',
            link=f'/dashboard/bookings/{booking.id}'
        )
        # Email — throttle: sólo si el último mensaje previo del sender→recipient en este booking
        # fue hace >15min, para no spammear durante chats activos.
        try:
            from django.utils import timezone as _tz
            from datetime import timedelta
            threshold = _tz.now() - timedelta(minutes=15)
            recent = Message.objects.filter(
                booking=booking, sender=msg.sender,
                created_at__gte=threshold
            ).exclude(pk=msg.pk).exists()
            if not recent:
                from accounts.emails import send_new_message_email
                # No filtres por flagged — si el msg fue sanitizado, mandamos el contenido limpio
                send_new_message_email(recipient, msg.sender, booking, msg.content)
        except Exception:
            pass


class MarkMessagesReadView(APIView):
    """Mark all messages in a booking as read for current user."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, booking_id):
        updated = Message.objects.filter(
            booking_id=booking_id, is_read=False
        ).exclude(sender=request.user).update(is_read=True)
        return Response({'marked_read': updated})


# ── Notification Views ──

class NotificationListView(generics.ListAPIView):
    """List notifications for the authenticated user."""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class NotificationMarkReadView(APIView):
    """Mark notification(s) as read."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        notification_ids = request.data.get('ids', [])
        if notification_ids:
            Notification.objects.filter(
                id__in=notification_ids, user=request.user
            ).update(is_read=True)
        else:
            # Mark all as read
            Notification.objects.filter(
                user=request.user, is_read=False
            ).update(is_read=True)
        return Response({'status': 'ok'})


class UnreadNotificationCountView(APIView):
    """Get count of unread notifications."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()
        return Response({'unread_count': count})


# ── Review Views ──

class ReviewCreateView(generics.CreateAPIView):
    """Create a review for a completed booking."""
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        from decimal import Decimal
        from .models import ClientCredit
        booking = Booking.objects.get(id=self.kwargs['booking_id'])
        if booking.status != 'completada':
            from rest_framework.exceptions import ValidationError
            raise ValidationError('Solo se pueden dejar reseñas en reservas completadas.')
        if hasattr(booking, 'review'):
            from rest_framework.exceptions import ValidationError
            raise ValidationError('Ya enviaste una reseña para esta reserva.')
        serializer.save(
            client=self.request.user,
            talent=booking.talent,
            booking=booking
        )
        # Recompensa: crédito de $50 al cliente por dejar reseña
        ClientCredit.objects.create(
            client=self.request.user,
            amount=Decimal('50.00'),
            reason='review_reward',
            booking=booking,
            note=f'Reseña en booking {booking.booking_code or booking.id}',
        )
        # Notify talent
        Notification.objects.create(
            user=booking.talent.user,
            notification_type='new_review',
            title='¡Nueva reseña!',
            message=f'{self.request.user.get_full_name()} dejó una reseña de {serializer.instance.rating}★.',
            link=f'/talent/{booking.talent.id}'
        )


class TalentReviewsView(generics.ListAPIView):
    """List all reviews for a specific talent."""
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Review.objects.filter(talent_id=self.kwargs['talent_id'])


class ClientCreditsView(APIView):
    """Saldo y lista de créditos del cliente autenticado."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from decimal import Decimal
        from .models import ClientCredit
        qs = ClientCredit.objects.filter(client=request.user)
        total = qs.filter(used=False).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        items = [{
            'id': c.id,
            'amount': str(c.amount),
            'reason': c.reason,
            'reason_display': c.get_reason_display(),
            'used': c.used,
            'note': c.note,
            'created_at': c.created_at.isoformat(),
        } for c in qs[:50]]
        return Response({'balance': str(total), 'credits': items})


# ── Cancellation policy preview ──
class CancellationPreviewView(APIView):
    """Preview del reembolso si se cancela ahora un booking dado."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)
        if booking.client != request.user and booking.talent.user != request.user:
            return Response({'error': 'Forbidden'}, status=403)
        return Response(booking.cancellation_refund())


# ── Review response (sólo Premium) ──
class ReviewResponseView(APIView):
    """Talento Premium puede responder a una reseña suya."""
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            review = Review.objects.get(pk=pk)
        except Review.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)
        # Sólo el talento dueño
        if review.talent.user != request.user:
            return Response({'error': 'Forbidden'}, status=403)
        # Gating por tier
        if review.talent.talent_level != 'premium':
            return Response({
                'error': 'Sólo los talentos Premium pueden responder a reseñas.'
            }, status=403)
        from django.utils import timezone as _tz
        response_text = request.data.get('response', '').strip()
        if not response_text:
            return Response({'error': 'response es requerido'}, status=400)
        review.response = response_text
        review.response_at = _tz.now()
        review.save(update_fields=['response', 'response_at'])
        return Response(ReviewSerializer(review).data)


# ── Premium Invitations (admin) ──
class PremiumInvitationListCreateView(generics.ListCreateAPIView):
    """Listar todas las invitaciones (admin) o crear una nueva."""
    serializer_class = PremiumInvitationSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return PremiumInvitation.objects.all()

    def perform_create(self, serializer):
        serializer.save(invited_by=self.request.user)
        # Notify talent
        inv = serializer.instance
        Notification.objects.create(
            user=inv.talent.user,
            notification_type='premium_invitation',
            title='¡Has sido invitado a Pulsar Premium!',
            message=inv.message or 'El equipo de Pulsar te invitó al tier Premium. Revisa tu dashboard.',
            link='/talent-dashboard'
        )


class PremiumInvitationActionView(APIView):
    """Talento acepta o rechaza su invitación."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            inv = PremiumInvitation.objects.get(pk=pk)
        except PremiumInvitation.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)
        if inv.talent.user != request.user:
            return Response({'error': 'Forbidden'}, status=403)
        if inv.status != 'pending':
            return Response({'error': f'Invitación ya {inv.get_status_display()}'}, status=400)
        action = request.data.get('action')
        if action == 'accept':
            inv.accept()
        elif action == 'decline':
            inv.decline()
        else:
            return Response({'error': 'action debe ser accept o decline'}, status=400)
        return Response(PremiumInvitationSerializer(inv).data)


class MyPremiumInvitationView(APIView):
    """El talento autenticado ve su invitación pendiente, si existe."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, 'talent_profile'):
            return Response({'invitation': None})
        inv = PremiumInvitation.objects.filter(
            talent=request.user.talent_profile, status='pending'
        ).first()
        if not inv:
            return Response({'invitation': None})
        return Response({'invitation': PremiumInvitationSerializer(inv).data})


# ── Flagged messages (admin) ──
class FlaggedMessagesView(generics.ListAPIView):
    """Admin: lista de mensajes que el scanner anti-disinter capturó."""
    serializer_class = FlaggedMessageSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return Message.objects.filter(flagged=True).select_related('sender', 'booking')


class FlaggedMessagesStatsView(APIView):
    """Stats agregadas: top usuarios con más violaciones, categorías más comunes."""
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        total = Message.objects.filter(flagged=True).count()
        # Top senders
        top_senders = (
            Message.objects.filter(flagged=True)
            .values('sender__id', 'sender__email', 'sender__first_name', 'sender__last_name')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )
        # Categorías más comunes (deserializa JSONField)
        from collections import Counter
        cats = Counter()
        for m in Message.objects.filter(flagged=True).values_list('flagged_categories', flat=True):
            for c in (m or []):
                cats[c] += 1
        return Response({
            'total_flagged': total,
            'top_senders': list(top_senders),
            'categories': dict(cats),
        })


# ── Talent payout dashboard ──
class TalentPayoutView(APIView):
    """Resumen de payouts del talento autenticado: total cobrado, próximo payout, breakdown por booking."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, 'talent_profile'):
            return Response({'error': 'No tienes perfil de talento'}, status=404)
        talent = request.user.talent_profile
        config = PlatformConfig.get_config()

        # Comisión según tier
        if talent.talent_level == 'premium':
            commission_rate = config.premium_commission_rate
        elif talent.talent_level == 'pro':
            commission_rate = config.pro_commission_rate
        else:
            commission_rate = config.standard_commission_rate

        bookings = talent.bookings.filter(status__in=['confirmada', 'completada'])

        total_gross = Decimal('0.00')
        total_net = Decimal('0.00')
        pending_net = Decimal('0.00')
        items = []
        for b in bookings.order_by('-event_date'):
            gross = Decimal(str(b.quoted_price or b.precio_estimado or 0))
            commission = (gross * commission_rate).quantize(Decimal('0.01'))
            net = gross - commission
            total_gross += gross
            if b.status == 'completada':
                total_net += net
            else:
                pending_net += net
            items.append({
                'booking_id': b.id,
                'booking_code': b.booking_code,
                'event_date': str(b.event_date),
                'event_type': b.event_type,
                'status': b.status,
                'gross': str(gross),
                'commission': str(commission),
                'net': str(net),
            })

        # Próximo tier upgrade
        next_tier = None
        progress = None
        if talent.talent_level == 'standard':
            event_count = talent.bookings.filter(status='completada').count()
            rating = Decimal(str(talent.rating_avg or 0))
            next_tier = 'pro'
            progress = {
                'events_done': event_count,
                'events_needed': config.auto_promote_min_events,
                'events_pct': min(100, int(event_count * 100 / config.auto_promote_min_events)) if config.auto_promote_min_events else 0,
                'rating_current': str(rating),
                'rating_needed': str(config.auto_promote_min_rating),
                'rating_pct': min(100, int(rating * 100 / config.auto_promote_min_rating)) if config.auto_promote_min_rating else 0,
                'eligible': (event_count >= config.auto_promote_min_events and rating >= config.auto_promote_min_rating),
            }
        elif talent.talent_level == 'pro':
            next_tier = 'premium'
            progress = {
                'note': 'Premium es por invitación de Pulsar. Mantén rating ≥4.7 y entrega impecable.',
                'invitation_only': True,
            }

        return Response({
            'tier': talent.talent_level,
            'commission_rate': str(commission_rate),
            'commission_pct': str((commission_rate * 100).quantize(Decimal('1'))),
            'total_gross': str(total_gross),
            'total_net': str(total_net),
            'pending_net': str(pending_net),
            'bookings_count': bookings.count(),
            'next_tier': next_tier,
            'progress': progress,
            'items': items[:20],
        })


# ── Reportar problema (Dispute) ──
class DisputeCreateView(generics.CreateAPIView):
    """Cliente reporta problema en un booking. Cambia status a 'en_disputa' y retiene el pago."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = None

    def create(self, request, *args, **kwargs):
        from django.utils import timezone as _tz
        booking_id = kwargs.get('booking_id')
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)
        if booking.client != request.user:
            return Response({'error': 'Forbidden'}, status=403)
        if booking.status not in ('confirmada', 'completada'):
            return Response({'error': 'Solo puedes reportar bookings confirmadas o completadas.'}, status=400)
        if hasattr(booking, 'dispute'):
            return Response({'error': 'Ya existe una disputa para este booking.'}, status=400)

        reason = request.data.get('reason')
        description = request.data.get('description', '').strip()
        if not reason or not description:
            return Response({'error': 'reason y description son requeridos.'}, status=400)

        dispute = Dispute.objects.create(
            booking=booking,
            reported_by=request.user,
            reason=reason,
            description=description,
        )
        booking.status = 'en_disputa'
        booking.save(update_fields=['status', 'updated_at'])

        # Notify talent + admins
        Notification.objects.create(
            user=booking.talent.user,
            notification_type='system',
            title='Disputa abierta en tu booking',
            message=f'El cliente reportó: {dispute.get_reason_display()}. Pulsar revisará.',
            link=f'/dashboard/bookings/{booking.id}'
        )
        return Response({
            'dispute_id': dispute.id,
            'status': dispute.status,
            'message': 'Disputa abierta. El pago al talento queda retenido. El equipo de Pulsar te contactará.'
        }, status=201)


# ── Modificar booking (cambiar fecha/hora) ──
class BookingModifyView(APIView):
    """Cliente solicita cambio de fecha/hora. Si pasa de 48h pre-evento, va a re-confirmación del talento."""
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        from datetime import datetime, timedelta
        from django.utils import timezone as _tz
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)
        if booking.client != request.user:
            return Response({'error': 'Forbidden'}, status=403)
        if booking.status not in ('aceptada', 'pendiente_pago', 'confirmada'):
            return Response({'error': 'No se puede modificar en este estado.'}, status=400)

        new_date = request.data.get('event_date')
        new_start = request.data.get('event_time_start')
        new_end = request.data.get('event_time_end')

        if not (new_date and new_start and new_end):
            return Response({'error': 'event_date, event_time_start y event_time_end requeridos.'}, status=400)

        booking.event_date = new_date
        booking.event_time_start = new_start
        booking.event_time_end = new_end
        # Si estaba confirmada, volver a pendiente_respuesta para que el talento reconfirme
        if booking.status == 'confirmada':
            booking.status = 'pendiente_respuesta'
        booking.save()

        Notification.objects.create(
            user=booking.talent.user,
            notification_type='system',
            title='Cambio en booking',
            message=f'El cliente solicitó nueva fecha: {new_date} {new_start}. Confirma o ajusta.',
            link=f'/dashboard/bookings/{booking.id}'
        )
        return Response(BookingDetailSerializer(booking).data)


# ── Admin: procesar refund ──
class AdminProcessRefundView(APIView):
    """Admin emite un reembolso. Crea ClientCredit y cierra la disputa si existe."""
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, booking_id):
        from .models import ClientCredit
        from django.utils import timezone as _tz
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)
        amount = Decimal(str(request.data.get('amount', '0')))
        if amount <= 0:
            return Response({'error': 'amount debe ser > 0'}, status=400)
        reason = request.data.get('reason', 'manual')
        note = request.data.get('note', '')

        ClientCredit.objects.create(
            client=booking.client,
            amount=amount,
            reason='refund',
            booking=booking,
            note=note or f'Reembolso emitido por admin para {booking.booking_code}',
        )

        # Si hay disputa abierta, resolverla
        dispute = getattr(booking, 'dispute', None)
        if dispute and dispute.status in ('open', 'investigating'):
            dispute.status = 'resolved_refund'
            dispute.resolved_by = request.user
            dispute.refund_amount = amount
            dispute.resolved_at = _tz.now()
            dispute.save()

        # Audit log
        AuditLog.objects.create(
            actor=request.user,
            action='booking_refund',
            target_type='booking',
            target_id=booking.id,
            details={'amount': str(amount), 'reason': reason, 'note': note},
            ip_address=request.META.get('REMOTE_ADDR'),
        )

        # Notify client
        Notification.objects.create(
            user=booking.client,
            notification_type='system',
            title='Reembolso emitido',
            message=f'Recibiste un crédito Pulsar de ${amount} por el booking {booking.booking_code}.',
            link='/dashboard'
        )
        return Response({'success': True, 'amount': str(amount)})


# ── Admin: lista de disputas ──
class DisputeListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = None

    def list(self, request):
        items = []
        for d in Dispute.objects.select_related('booking', 'reported_by').order_by('-created_at')[:100]:
            items.append({
                'id': d.id,
                'booking_id': d.booking_id,
                'booking_code': d.booking.booking_code,
                'reported_by_name': d.reported_by.get_full_name() if d.reported_by else '—',
                'reason': d.reason,
                'reason_display': d.get_reason_display(),
                'description': d.description,
                'status': d.status,
                'status_display': d.get_status_display(),
                'admin_notes': d.admin_notes,
                'refund_amount': str(d.refund_amount) if d.refund_amount else None,
                'created_at': d.created_at.isoformat(),
                'resolved_at': d.resolved_at.isoformat() if d.resolved_at else None,
            })
        return Response(items)


# ── Booking contract (HTML descargable) ──
class BookingContractView(APIView):
    """Genera un contrato HTML del booking. El cliente lo puede imprimir/guardar como PDF."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, booking_id):
        from django.http import HttpResponse
        try:
            booking = Booking.objects.select_related('client', 'talent').get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)
        # Solo participantes
        if booking.client != request.user and booking.talent.user != request.user:
            return Response({'error': 'Forbidden'}, status=403)

        gross = booking.quoted_price or booking.precio_estimado or Decimal('0.00')
        total = booking.total_to_pay

        html = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8"><title>Contrato {booking.booking_code}</title>
<style>
  body {{ font-family: -apple-system, sans-serif; max-width: 720px; margin: 40px auto; padding: 0 24px; color: #222; line-height: 1.6; }}
  h1 {{ font-size: 22px; border-bottom: 2px solid #c8f04a; padding-bottom: 8px; }}
  h2 {{ font-size: 16px; margin-top: 28px; color: #555; }}
  .code {{ display: inline-block; padding: 4px 12px; background: #f5f5f0; border-radius: 4px; font-family: monospace; color: #6b8a0f; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 8px; }}
  td {{ padding: 8px 0; border-bottom: 1px solid #eee; font-size: 14px; }}
  td:first-child {{ color: #777; width: 40%; }}
  .total {{ font-size: 18px; font-weight: 700; color: #6b8a0f; }}
  .footer {{ margin-top: 40px; padding-top: 16px; border-top: 1px solid #ddd; font-size: 12px; color: #999; }}
  .sig {{ margin-top: 60px; display: flex; gap: 40px; }}
  .sig div {{ flex: 1; text-align: center; }}
  .sig hr {{ border: none; border-top: 1px solid #333; margin-bottom: 6px; }}
  @media print {{ body {{ margin: 20px auto; }} }}
</style></head><body>
<h1>Contrato de Servicio · Pulsar</h1>
<p><strong>Código:</strong> <span class="code">{booking.booking_code}</span></p>

<h2>Partes</h2>
<table>
  <tr><td>Cliente</td><td>{booking.client.get_full_name() or booking.client.email}</td></tr>
  <tr><td>Talento</td><td>{booking.talent.stage_name} ({booking.talent.get_talent_type_display()})</td></tr>
  <tr><td>Tier</td><td>{booking.talent.get_talent_level_display()}</td></tr>
</table>

<h2>Detalles del evento</h2>
<table>
  <tr><td>Tipo</td><td>{booking.get_event_type_display()}</td></tr>
  <tr><td>Nombre</td><td>{booking.event_name or '—'}</td></tr>
  <tr><td>Fecha</td><td>{booking.event_date}</td></tr>
  <tr><td>Horario</td><td>{booking.event_time_start} — {booking.event_time_end}</td></tr>
  <tr><td>Duración</td><td>{booking.event_duration_hours or '—'} hrs</td></tr>
  <tr><td>Ubicación</td><td>{booking.event_location}{', ' + booking.event_city if booking.event_city else ''}</td></tr>
  <tr><td>Invitados estimados</td><td>{booking.guest_count or '—'}</td></tr>
</table>

<h2>Términos económicos</h2>
<table>
  <tr><td>Performance del talento</td><td>${gross:.2f}</td></tr>
  <tr><td>Tarifa Pulsar (gestión)</td><td>${booking.service_fee or 0:.2f}</td></tr>
  <tr><td>ITBMS 7%</td><td>${booking.tax_amount or 0:.2f}</td></tr>
  <tr><td class="total">Total a pagar</td><td class="total">${total:.2f}</td></tr>
</table>

<h2>Términos y condiciones</h2>
<p style="font-size: 13px;">
  El cliente paga el monto total a Pulsar, que lo retiene en custodia (escrow) hasta 24 horas después del evento.
  Si el talento no se presenta, el cliente recibe reembolso del 100%.
  Política de cancelación: más de 7 días antes 100% reembolso, entre 2-7 días 50%, menos de 48h sin reembolso.
  Toda comunicación entre las partes debe realizarse dentro de la plataforma Pulsar.
</p>

<div class="sig">
  <div><hr><span>Cliente</span></div>
  <div><hr><span>Talento</span></div>
</div>

<div class="footer">
  Generado por Pulsar by ShowRoots el {booking.updated_at:%Y-%m-%d %H:%M}. Documento de referencia, no constituye obligación legal directa.
</div>
</body></html>"""

        response = HttpResponse(html, content_type='text/html')
        response['Content-Disposition'] = f'attachment; filename="contrato-{booking.booking_code}.html"'
        return response


# ── Admin: bookings export CSV ──
class BookingsExportCSV(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="bookings.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Code', 'Client', 'Talent', 'Event Type', 'Event Date', 'Status',
            'Quoted Price', 'Service Fee', 'Tax', 'Amount Paid', 'Created At'
        ])
        for b in Booking.objects.select_related('client', 'talent').order_by('-created_at')[:5000]:
            writer.writerow([
                b.booking_code, b.client.get_full_name(), b.talent.stage_name,
                b.event_type, b.event_date, b.status,
                b.quoted_price or '', b.service_fee or '', b.tax_amount or '',
                b.amount_paid or '', b.created_at.isoformat(),
            ])
        AuditLog.objects.create(
            actor=request.user,
            action='other',
            target_type='bookings_export',
            details={'rows_exported': 'up_to_5000'},
        )
        return response


# ── Partner Views ──

class PartnerDashboardView(APIView):
    """Dashboard statistics for the Partner role."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != 'partner':
            return Response(
                {'error': 'Solo los Partners pueden acceder a este dashboard.'},
                status=status.HTTP_403_FORBIDDEN
            )

        partner_bookings = Booking.objects.filter(partner=user)

        total_bookings = partner_bookings.count()
        active_bookings = partner_bookings.filter(
            status__in=['solicitud_enviada', 'pendiente_respuesta', 'aceptada', 'pendiente_pago', 'confirmada']
        ).count()
        completed_bookings = partner_bookings.filter(status='completada').count()

        # Commission earned from completed payments
        total_commission = Payment.objects.filter(
            booking__partner=user,
            payment_status='completed'
        ).aggregate(total=Sum('commission_partner'))['total'] or Decimal('0.00')

        # Pending commission from active bookings
        pending_commission = Payment.objects.filter(
            booking__partner=user,
            payment_status='pending'
        ).aggregate(total=Sum('commission_partner'))['total'] or Decimal('0.00')

        stats = {
            'total_bookings': total_bookings,
            'active_bookings': active_bookings,
            'completed_bookings': completed_bookings,
            'total_commission_earned': total_commission,
            'pending_commission': pending_commission,
        }

        # Also return recent bookings
        recent_bookings = BookingListSerializer(
            partner_bookings.order_by('-created_at')[:10], many=True
        ).data

        return Response({
            'stats': PartnerStatsSerializer(stats).data,
            'recent_bookings': recent_bookings,
        })


# ── Admin Config ──

class PlatformConfigView(APIView):
    """GET/PUT platform configuration (admin only)."""
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        config = PlatformConfig.get_config()
        return Response(PlatformConfigSerializer(config).data)

    def put(self, request):
        config = PlatformConfig.get_config()
        serializer = PlatformConfigSerializer(config, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
