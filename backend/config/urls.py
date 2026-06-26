"""
URL configuration for WebDJ
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from accounts.admin_views import (
    AdminTalentListView, AdminTalentUpdateView,
    AdminBookingListView, AdminUserListView, AdminPaymentListView,
)

# Personalización del admin de Django (en español)
admin.site.site_header = 'Pulsar — Panel de Administración'
admin.site.site_title = 'Pulsar Admin'
admin.site.index_title = 'Gestión de la plataforma'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/', include('talents.urls')),
    path('api/', include('bookings.urls')),
    path('api/', include('venues.urls')),
    path('api/', include('payments.urls')),
    # Admin API
    path('api/admin/talents/', AdminTalentListView.as_view(), name='admin-talents'),
    path('api/admin/talents/<int:pk>/', AdminTalentUpdateView.as_view(), name='admin-talent-update'),
    path('api/admin/bookings/', AdminBookingListView.as_view(), name='admin-bookings'),
    path('api/admin/users/', AdminUserListView.as_view(), name='admin-users'),
    path('api/admin/payments/', AdminPaymentListView.as_view(), name='admin-payments'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
