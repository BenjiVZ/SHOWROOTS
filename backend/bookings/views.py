from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Booking, Payment, Message, Notification, Review, PlatformConfig
from .serializers import (
    BookingListSerializer, BookingDetailSerializer,
    BookingCreateSerializer, ReviewSerializer,
    PaymentSerializer, PaymentCreateSerializer,
    MessageSerializer, MessageCreateSerializer,
    NotificationSerializer, PartnerStatsSerializer,
    PlatformConfigSerializer,
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
        booking = Booking.objects.get(id=self.kwargs['booking_id'])
        if booking.status != 'completada':
            from rest_framework.exceptions import ValidationError
            raise ValidationError('Solo se pueden dejar reseñas en reservas completadas.')
        serializer.save(
            client=self.request.user,
            talent=booking.talent,
            booking=booking
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
