from rest_framework import generics, permissions, status, parsers
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Genre, TalentProfile, TalentMedia, TalentExperience, Availability
from .serializers import (
    GenreSerializer, TalentListSerializer, TalentDetailSerializer,
    TalentCreateSerializer, TalentMediaSerializer, TalentExperienceSerializer,
    AvailabilitySerializer, AvailabilityCreateSerializer,
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
    """Create a talent profile for the authenticated user."""
    serializer_class = TalentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class TalentUpdateView(generics.UpdateAPIView):
    """Update own talent profile."""
    serializer_class = TalentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_object(self):
        return TalentProfile.objects.get(user=self.request.user)


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
            'cover_photo': request.build_absolute_uri(talent.cover_photo.url)
        })


class TalentMediaListCreateView(generics.ListCreateAPIView):
    """List or upload media for a talent profile."""
    serializer_class = TalentMediaSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_queryset(self):
        return TalentMedia.objects.filter(talent_id=self.kwargs['talent_id'])

    def perform_create(self, serializer):
        talent = TalentProfile.objects.get(id=self.kwargs['talent_id'])
        serializer.save(talent=talent)


class TalentMediaDeleteView(generics.DestroyAPIView):
    """Delete a media item."""
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
