from rest_framework import generics, permissions, status, parsers
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Genre, TalentProfile, TalentMedia, TalentExperience, Availability, Pack, TalentFAQ
from .serializers import (
    GenreSerializer, TalentListSerializer, TalentDetailSerializer,
    TalentCreateSerializer, TalentMediaSerializer, TalentExperienceSerializer,
    AvailabilitySerializer, AvailabilityCreateSerializer,
    PackSerializer, TalentFAQSerializer,
)
from .filters import TalentFilter


class GenreListView(generics.ListAPIView):
    """List all available music genres."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = None


class TalentListView(generics.ListAPIView):
    """List talents with search and filters. Only approved talents are shown."""
    serializer_class = TalentListSerializer
    filterset_class = TalentFilter
    search_fields = ['stage_name', 'tagline', 'description', 'city', 'genres__name']
    ordering_fields = [
        'rating_avg', 'hourly_rate', 'price_min',
        'experience_years', 'created_at', 'total_bookings'
    ]

    def get_queryset(self):
        return TalentProfile.objects.filter(
            is_approved=True
        ).select_related('user').prefetch_related('genres')


class TalentDetailView(generics.RetrieveAPIView):
    """Get a talent profile detail."""
    queryset = TalentProfile.objects.select_related('user').prefetch_related(
        'genres', 'media', 'experiences', 'availability'
    )
    serializer_class = TalentDetailSerializer


class TalentCreateView(generics.CreateAPIView):
    """Create a talent profile for the authenticated user.

    Si ya existe un perfil, hace upsert (actualiza el existente) en lugar de fallar.
    Esto evita 500 errors si el DJ reintenta el wizard de onboarding.
    """
    serializer_class = TalentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        existing = TalentProfile.objects.filter(user=request.user).first()
        if existing:
            # Upsert: actualizar el perfil existente con los datos del wizard
            serializer = self.get_serializer(existing, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return super().create(request, *args, **kwargs)


class TalentUpdateView(generics.RetrieveUpdateAPIView):
    """Retrieve and update own talent profile."""
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return TalentCreateSerializer
        return TalentDetailSerializer

    def get_object(self):
        try:
            return TalentProfile.objects.select_related('user').prefetch_related(
                'genres', 'media', 'experiences', 'availability'
            ).get(user=self.request.user)
        except TalentProfile.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound('No tienes perfil de talento. Crea uno primero.')


class CoverPhotoUploadView(APIView):
    """Upload or update a talent's cover photo."""
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request):
        try:
            talent = request.user.talent_profile
        except TalentProfile.DoesNotExist:
            return Response({'error': 'No tienes perfil de talento.'}, status=status.HTTP_400_BAD_REQUEST)

        photo = request.FILES.get('cover_photo')
        if not photo:
            return Response({'error': 'No se proporcionó ninguna imagen.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate file type
        allowed = ['image/jpeg', 'image/png', 'image/webp']
        if photo.content_type not in allowed:
            return Response({'error': 'Solo se permiten imágenes JPG, PNG o WebP.'}, status=status.HTTP_400_BAD_REQUEST)

        # Delete old photo if exists
        if talent.cover_photo:
            talent.cover_photo.delete(save=False)

        talent.cover_photo = photo
        talent.save(update_fields=['cover_photo'])

        return Response({
            'message': 'Foto de portada actualizada.',
            'cover_photo': talent.cover_photo.url,
        })


class TalentMediaListCreateView(generics.ListCreateAPIView):
    """List or upload media for a talent profile."""
    serializer_class = TalentMediaSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_queryset(self):
        return TalentMedia.objects.filter(talent_id=self.kwargs['talent_id'])

    def perform_create(self, serializer):
        from rest_framework.exceptions import PermissionDenied
        from .tier_limits import can_add
        talent = TalentProfile.objects.get(id=self.kwargs['talent_id'])
        if talent.user != self.request.user:
            raise PermissionDenied('Solo el dueño puede subir media.')
        # Map media_type to kind
        media_type = serializer.validated_data.get('media_type')
        kind_map = {'photo': 'photo', 'audio': 'mix', 'video': 'video'}
        kind = kind_map.get(media_type)
        if kind:
            allowed, limit, current = can_add(talent, kind)
            if not allowed:
                raise PermissionDenied(
                    f'Tu Plan {talent.get_talent_level_display()} permite máximo {limit} {kind}s. '
                    f'Haz upgrade de Plan para subir más.'
                )
        serializer.save(talent=talent)


class TalentMediaDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update (title/order/is_cover), or delete a media item owned by the requesting user."""
    serializer_class = TalentMediaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TalentMedia.objects.filter(talent__user=self.request.user)


class TalentExperienceListCreateView(generics.ListCreateAPIView):
    """List or add experience for a talent."""
    serializer_class = TalentExperienceSerializer

    def get_queryset(self):
        return TalentExperience.objects.filter(talent_id=self.kwargs['talent_id'])

    def perform_create(self, serializer):
        talent = TalentProfile.objects.get(id=self.kwargs['talent_id'])
        serializer.save(talent=talent)


class FeaturedTalentsView(generics.ListAPIView):
    """List featured talents for the homepage (premium first)."""
    serializer_class = TalentListSerializer
    pagination_class = None

    def get_queryset(self):
        return TalentProfile.objects.filter(
            is_featured=True, is_available=True, is_approved=True
        ).select_related('user').prefetch_related('genres')[:8]


# ── Availability Views ──

class AvailabilityListView(generics.ListAPIView):
    """List talent's availability calendar."""
    serializer_class = AvailabilitySerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Availability.objects.filter(talent_id=self.kwargs['talent_id'])


class AvailabilityManageView(APIView):
    """Manage own availability (create/update dates)."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            talent = request.user.talent_profile
        except TalentProfile.DoesNotExist:
            return Response(
                {'error': 'No tienes un perfil de talento.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = AvailabilityCreateSerializer(
            data=request.data,
            context={'talent': talent}
        )
        serializer.is_valid(raise_exception=True)
        availability = serializer.save()
        return Response(
            AvailabilitySerializer(availability).data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request):
        try:
            talent = request.user.talent_profile
        except TalentProfile.DoesNotExist:
            return Response(
                {'error': 'No tienes un perfil de talento.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        date = request.data.get('date')
        if date:
            Availability.objects.filter(talent=talent, date=date).delete()
            return Response({'status': 'ok'})
        return Response(
            {'error': 'Fecha requerida.'},
            status=status.HTTP_400_BAD_REQUEST
        )


class StatsView(APIView):
    """Public statistics for the platform."""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        from bookings.models import Booking
        return Response({
            'total_talents': TalentProfile.objects.filter(is_available=True, is_approved=True).count(),
            'total_djs': TalentProfile.objects.filter(talent_type='dj', is_available=True, is_approved=True).count(),
            'total_musicians': TalentProfile.objects.filter(talent_type='musician', is_available=True, is_approved=True).count(),
            'total_bands': TalentProfile.objects.filter(talent_type='band', is_available=True, is_approved=True).count(),
            'total_bookings': Booking.objects.filter(status='completada').count(),
            'total_genres': Genre.objects.count(),
            'premium_talents': TalentProfile.objects.filter(talent_level='premium', is_approved=True).count(),
        })


class TalentInquiryView(APIView):
    """Cliente envía una consulta rápida al talento sin crear booking aún."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, talent_id):
        try:
            talent = TalentProfile.objects.get(id=talent_id)
        except TalentProfile.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)

        message = (request.data.get('message') or '').strip()
        if len(message) < 10:
            return Response({'error': 'Mensaje debe tener al menos 10 caracteres.'}, status=400)

        # Anti-disinter scan
        from bookings.anti_disinter import sanitize
        clean, findings = sanitize(message)
        if findings:
            return Response({
                'error': 'Tu mensaje contiene patrones de contacto directo. Toda comunicación queda dentro de Pulsar.',
                'categories': list({cat for cat, _ in findings}),
            }, status=400)

        # Crear notificación al talento
        from bookings.models import Notification
        Notification.objects.create(
            user=talent.user,
            notification_type='new_message',
            title=f'Nueva consulta de {request.user.get_full_name() or request.user.email}',
            message=clean[:500],
            link=f'/talent-dashboard'
        )
        return Response({'success': True, 'message': 'Consulta enviada. El talento responderá pronto.'})


class MyTierLimitsView(APIView):
    """Devuelve los límites del tier del talento autenticado + lo que ya consumió."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from .tier_limits import get_limits, can_add
        if not hasattr(request.user, 'talent_profile'):
            return Response({'error': 'No tienes perfil de talento'}, status=404)
        talent = request.user.talent_profile
        limits = get_limits(talent.talent_level)
        usage = {}
        for kind in ['photo', 'mix', 'video', 'pack', 'faq']:
            allowed, limit, current = can_add(talent, kind)
            usage[kind] = {'limit': limit, 'current': current, 'can_add': allowed}
        return Response({
            'tier': talent.talent_level,
            'limits': limits,
            'usage': usage,
        })


# ── Packs ─────────────────────────────────────────────────────────
class PackListCreateView(generics.ListCreateAPIView):
    """List packs of a talent (public read) or create one (owner)."""
    serializer_class = PackSerializer

    def get_queryset(self):
        return Pack.objects.filter(talent_id=self.kwargs['talent_id'])

    def perform_create(self, serializer):
        from rest_framework.exceptions import PermissionDenied
        from .tier_limits import can_add
        talent = TalentProfile.objects.get(id=self.kwargs['talent_id'])
        if talent.user != self.request.user:
            raise PermissionDenied('Solo el dueño puede crear paquetes.')
        allowed, limit, current = can_add(talent, 'pack')
        if not allowed:
            raise PermissionDenied(
                f'Tu Plan {talent.get_talent_level_display()} permite máximo {limit} paquete(s).'
            )
        serializer.save(talent=talent)


class PackDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a pack (owner only for write)."""
    serializer_class = PackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Pack.objects.filter(talent__user=self.request.user)


# ── FAQs ─────────────────────────────────────────────────────────
class FAQListCreateView(generics.ListCreateAPIView):
    """List FAQs of a talent (public read) or create one (owner)."""
    serializer_class = TalentFAQSerializer

    def get_queryset(self):
        return TalentFAQ.objects.filter(talent_id=self.kwargs['talent_id'])

    def perform_create(self, serializer):
        from rest_framework.exceptions import PermissionDenied
        from .tier_limits import can_add
        talent = TalentProfile.objects.get(id=self.kwargs['talent_id'])
        if talent.user != self.request.user:
            raise PermissionDenied('Solo el dueño puede crear FAQs.')
        allowed, limit, current = can_add(talent, 'faq')
        if not allowed:
            raise PermissionDenied(
                f'Tu Plan {talent.get_talent_level_display()} permite máximo {limit} FAQ(s).'
            )
        serializer.save(talent=talent)


class FAQDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an FAQ (owner only for write)."""
    serializer_class = TalentFAQSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TalentFAQ.objects.filter(talent__user=self.request.user)
