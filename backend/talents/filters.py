import django_filters
from .models import TalentProfile


class TalentFilter(django_filters.FilterSet):
    """Filters for searching talents."""

    talent_type = django_filters.ChoiceFilter(choices=TalentProfile.TALENT_TYPE_CHOICES)
    talent_level = django_filters.ChoiceFilter(choices=TalentProfile.TALENT_LEVEL_CHOICES)
    genre = django_filters.CharFilter(field_name='genres__slug', lookup_expr='exact')
    city = django_filters.CharFilter(lookup_expr='icontains')
    country = django_filters.CharFilter(lookup_expr='icontains')
    price_min = django_filters.NumberFilter(field_name='hourly_rate', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='hourly_rate', lookup_expr='lte')
    experience_min = django_filters.NumberFilter(field_name='experience_years', lookup_expr='gte')
    rating_min = django_filters.NumberFilter(field_name='rating_avg', lookup_expr='gte')
    is_available = django_filters.BooleanFilter()
    is_featured = django_filters.BooleanFilter()
    equipment = django_filters.BooleanFilter(field_name='equipment_own')

    class Meta:
        model = TalentProfile
        fields = [
            'talent_type', 'talent_level', 'genre', 'city', 'country',
            'price_min', 'price_max', 'experience_min',
            'rating_min', 'is_available', 'is_featured', 'equipment'
        ]
