from django.urls import path
from . import views

urlpatterns = [
    # Bookings
    path('bookings/', views.BookingListView.as_view(), name='booking-list'),
    path('bookings/create/', views.BookingCreateView.as_view(), name='booking-create'),
    path('bookings/<int:pk>/', views.BookingDetailView.as_view(), name='booking-detail'),
    path('bookings/<int:pk>/status/', views.BookingUpdateStatusView.as_view(), name='booking-status'),

    # Payments
    path('payments/create/', views.PaymentCreateView.as_view(), name='payment-create'),
    path('bookings/<int:booking_id>/payments/', views.BookingPaymentsView.as_view(), name='booking-payments'),

    # Messages
    path('bookings/<int:booking_id>/messages/', views.MessageListView.as_view(), name='booking-messages'),
    path('messages/send/', views.MessageCreateView.as_view(), name='message-send'),
    path('bookings/<int:booking_id>/messages/read/', views.MarkMessagesReadView.as_view(), name='messages-read'),

    # Notifications
    path('notifications/', views.NotificationListView.as_view(), name='notification-list'),
    path('notifications/read/', views.NotificationMarkReadView.as_view(), name='notification-read'),
    path('notifications/unread-count/', views.UnreadNotificationCountView.as_view(), name='notification-unread'),

    # Reviews
    path('bookings/<int:booking_id>/review/', views.ReviewCreateView.as_view(), name='booking-review'),
    path('talents/<int:talent_id>/reviews/', views.TalentReviewsView.as_view(), name='talent-reviews'),

    # Partner
    path('partner/dashboard/', views.PartnerDashboardView.as_view(), name='partner-dashboard'),

    # Admin Config
    path('admin/config/', views.PlatformConfigView.as_view(), name='platform-config'),
]
