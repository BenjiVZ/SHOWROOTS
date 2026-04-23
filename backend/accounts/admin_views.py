"""
Admin API views for frontend admin dashboard.
These endpoints require the user to have role='admin'.
"""
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from bookings.models import Booking, Payment, Notification
from bookings.serializers import BookingListSerializer, PaymentSerializer
from talents.models import TalentProfile
from talents.serializers import TalentListSerializer
from accounts.models import User
from accounts.serializers import UserSerializer


class IsAdmin(permissions.BasePermission):
    """Only admin users can access these endpoints."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


# ── Talent Management ──

class AdminTalentListView(generics.ListAPIView):
    """List all talent profiles for admin management."""
    serializer_class = TalentListSerializer
    permission_classes = [IsAdmin]
    queryset = TalentProfile.objects.select_related('user').all().order_by('-created_at')


class AdminTalentUpdateView(APIView):
    """Update talent profile (approve, change level, feature)."""
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        try:
            talent = TalentProfile.objects.get(pk=pk)
        except TalentProfile.DoesNotExist:
            return Response({'detail': 'Talento no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if 'is_approved' in request.data:
            talent.is_approved = request.data['is_approved']
        if 'talent_level' in request.data:
            talent.talent_level = request.data['talent_level']
        if 'is_featured' in request.data:
            talent.is_featured = request.data['is_featured']

        talent.save()

        # Notify talent on approval
        if request.data.get('is_approved'):
            Notification.objects.create(
                user=talent.user,
                notification_type='system',
                title='¡Tu perfil fue aprobado!',
                message='Un administrador ha aprobado tu perfil. Ya eres visible en la plataforma.',
                link=f'/talent/{talent.id}'
            )

        return Response(TalentListSerializer(talent).data)


# ── Booking Management ──

class AdminBookingListView(generics.ListAPIView):
    """List all bookings for admin oversight."""
    serializer_class = BookingListSerializer
    permission_classes = [IsAdmin]
    queryset = Booking.objects.select_related(
        'client', 'talent', 'talent__user', 'partner'
    ).all().order_by('-created_at')


# ── User Management ──

class AdminUserListView(generics.ListAPIView):
    """List all users."""
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    queryset = User.objects.all().order_by('-date_joined')


# ── Payment Management ──

class AdminPaymentListView(generics.ListAPIView):
    """List all payments."""
    serializer_class = PaymentSerializer
    permission_classes = [IsAdmin]
    queryset = Payment.objects.select_related('booking', 'client').all().order_by('-created_at')
