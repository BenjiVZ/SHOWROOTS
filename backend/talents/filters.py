import django_filters
from .models import TalentProfile


class TalentFilter(django_filters.FilterSet):
    """Filters for searching talents."""

    talent_type = django_filters.ChoiceFilter(choices=TalentProfile.TALENT_TYPE_CHOICES)
    talent_level = django_filters.ChoiceFilter(choices=TalentProfile.TALENT_LEVEL_CHOICES)
    experience_level = django_filters.ChoiceFilter(choices=TalentProfile.EXPERIENCE_LEVEL_CHOICES)
    genre = django_filters.CharFilter(field_name='genres__slug', lookup_expr='exact')
    genres = django_filters.CharFilter(method='filter_genres')  # comma-separated slugs
    city = django_filters.CharFilter(lookup_expr='icontains')
    country = django_filters.CharFilter(lookup_expr='icontains')
    price_min = django_filters.NumberFilter(field_name='hourly_rate', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='hourly_rate', lookup_expr='lte')
    experience_min = django_filters.NumberFilter(field_name='experience_years', lookup_expr='gte')
    rating_min = django_filters.NumberFilter(field_name='rating_avg', lookup_expr='gte')
    is_available = django_filters.BooleanFilter()
    is_featured = django_filters.BooleanFilter()
    equipment = django_filters.BooleanFilter(field_name='equipment_own')

    # Filtros nuevos sobre campos JSONField (búsqueda por contains)
    languages = django_filters.CharFilter(method='filter_languages')
    event_types = django_filters.CharFilter(method='filter_event_types')
    moods = django_filters.CharFilter(method='filter_moods')

    def filter_languages(self, queryset, name, value):
        """Comma-separated list. Match si CUALQUIERA está en languages."""
        items = [v.strip() for v in value.split(',') if v.strip()]
        if not items:
            return queryset
        q = None
        for item in items:
            sub = queryset.filter(languages__icontains=item)
            q = sub if q is None else (q | sub)
        return q.distinct() if q is not None else queryset

    def filter_event_types(self, queryset, name, value):
        """Comma-separated slugs. Match si CUALQUIERO está en event_types."""
        items = [v.strip() for v in value.split(',') if v.strip()]
        if not items:
            return queryset
        q = None
        for item in items:
            sub = queryset.filter(event_types__icontains=item)
            q = sub if q is None else (q | sub)
        return q.distinct() if q is not None else queryset

    def filter_moods(self, queryset, name, value):
        """Comma-separated mood tags."""
        items = [v.strip() for v in value.split(',') if v.strip()]
        if not items:
            return queryset
        q = None
        for item in items:
            sub = queryset.filter(mood_tags__icontains=item)
            q = sub if q is None else (q | sub)
        return q.distinct() if q is not None else queryset

    def filter_genres(self, queryset, name, value):
        """Comma-separated slugs — match si CUALQUIERO de los géneros coincide."""
        items = [v.strip() for v in value.split(',') if v.strip()]
        if not items:
            return queryset
        return queryset.filter(genres__slug__in=items).distinct()

    class Meta:
        model = TalentProfile
        fields = [
            'talent_type', 'talent_level', 'experience_level', 'genre', 'genres',
            'city', 'country', 'price_min', 'price_max', 'experience_min',
            'rating_min', 'is_available', 'is_featured', 'equipment',
            'languages', 'event_types', 'moods',
        ]
