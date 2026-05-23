from django.urls import path
from . import views

urlpatterns = [
    path('genres/', views.GenreListView.as_view(), name='genre-list'),
    path('talents/', views.TalentListView.as_view(), name='talent-list'),
    path('talents/create/', views.TalentCreateView.as_view(), name='talent-create'),
    path('talents/me/', views.TalentUpdateView.as_view(), name='talent-update-me'),
    path('talents/me/cover-photo/', views.CoverPhotoUploadView.as_view(), name='talent-cover-photo'),
    path('talents/<int:pk>/', views.TalentDetailView.as_view(), name='talent-detail'),
    path('talents/<int:talent_id>/media/', views.TalentMediaListCreateView.as_view(), name='talent-media'),
    path('talents/media/<int:pk>/', views.TalentMediaDeleteView.as_view(), name='talent-media-delete'),
    path('talents/<int:talent_id>/experiences/', views.TalentExperienceListCreateView.as_view(), name='talent-experiences'),
    # Availability
    path('talents/<int:talent_id>/availability/', views.AvailabilityListView.as_view(), name='talent-availability'),
    path('availability/manage/', views.AvailabilityManageView.as_view(), name='availability-manage'),
    # Packs
    path('talents/<int:talent_id>/packs/', views.PackListCreateView.as_view(), name='talent-packs'),
    path('talents/packs/<int:pk>/', views.PackDetailView.as_view(), name='pack-detail'),
    # FAQs
    path('talents/<int:talent_id>/faqs/', views.FAQListCreateView.as_view(), name='talent-faqs'),
    path('talents/faqs/<int:pk>/', views.FAQDetailView.as_view(), name='faq-detail'),
    # Homepage
    path('featured/', views.FeaturedTalentsView.as_view(), name='featured-talents'),
    path('stats/', views.StatsView.as_view(), name='stats'),

    # Tier limits
    path('talents/me/tier-limits/', views.MyTierLimitsView.as_view(), name='my-tier-limits'),

    # Inquiry (consulta rápida)
    path('talents/<int:talent_id>/inquire/', views.TalentInquiryView.as_view(), name='talent-inquire'),
]
