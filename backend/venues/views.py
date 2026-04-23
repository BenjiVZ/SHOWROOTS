from rest_framework import generics, permissions
from .models import Venue
from .serializers import VenueListSerializer, VenueDetailSerializer
import django_filters


class VenueFilter(django_filters.FilterSet):
    venue_type = django_filters.ChoiceFilter(choices=Venue.VENUE_TYPE_CHOICES)
    city = django_filters.CharFilter(lookup_expr='icontains')
    capacity_min = django_filters.NumberFilter(field_name='capacity_max', lookup_expr='gte')
    capacity_max = django_filters.NumberFilter(field_name='capacity_max', lookup_expr='lte')
    price_range = django_filters.CharFilter()

    class Meta:
        model = Venue
        fields = ['venue_type', 'city', 'capacity_min', 'capacity_max', 'price_range']


class VenueListView(generics.ListAPIView):
    """List active venues with filters."""
    queryset = Venue.objects.filter(is_active=True)
    serializer_class = VenueListSerializer
    filterset_class = VenueFilter
    search_fields = ['name', 'city', 'description', 'address']
    ordering_fields = ['rating_avg', 'name', 'capacity_max']


class VenueDetailView(generics.RetrieveAPIView):
    """Get venue details with photos."""
    queryset = Venue.objects.prefetch_related('photos').filter(is_active=True)
    serializer_class = VenueDetailSerializer
