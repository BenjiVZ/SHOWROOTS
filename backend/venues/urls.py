from django.urls import path
from . import views

urlpatterns = [
    path('venues/', views.VenueListView.as_view(), name='venue-list'),
    path('venues/<int:pk>/', views.VenueDetailView.as_view(), name='venue-detail'),
]
