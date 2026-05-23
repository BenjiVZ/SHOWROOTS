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

    # Client credits
    path('credits/', views.ClientCreditsView.as_view(), name='client-credits'),

    # Cancellation policy
    path('bookings/<int:booking_id>/cancel-preview/', views.CancellationPreviewView.as_view(), name='booking-cancel-preview'),

    # Review response (Premium only)
    path('reviews/<int:pk>/response/', views.ReviewResponseView.as_view(), name='review-response'),

    # Premium invitations
    path('premium/invitations/', views.PremiumInvitationListCreateView.as_view(), name='premium-invitations'),
    path('premium/invitations/<int:pk>/action/', views.PremiumInvitationActionView.as_view(), name='premium-invitation-action'),
    path('premium/my-invitation/', views.MyPremiumInvitationView.as_view(), name='my-premium-invitation'),

    # Admin flagged messages
    path('admin/flagged-messages/', views.FlaggedMessagesView.as_view(), name='admin-flagged-messages'),
    path('admin/flagged-messages/stats/', views.FlaggedMessagesStatsView.as_view(), name='admin-flagged-stats'),

    # Talent payout
    path('talents/me/payout/', views.TalentPayoutView.as_view(), name='talent-payout'),

    # Disputes / modify / contract / admin refund / CSV
    path('bookings/<int:booking_id>/dispute/', views.DisputeCreateView.as_view(), name='booking-dispute'),
    path('bookings/<int:pk>/modify/', views.BookingModifyView.as_view(), name='booking-modify'),
    path('bookings/<int:booking_id>/contract/', views.BookingContractView.as_view(), name='booking-contract'),
    path('admin/bookings/<int:booking_id>/refund/', views.AdminProcessRefundView.as_view(), name='admin-refund'),
    path('admin/disputes/', views.DisputeListView.as_view(), name='admin-disputes'),
    path('admin/bookings/export/', views.BookingsExportCSV.as_view(), name='admin-bookings-export'),

    # Partner
    path('partner/dashboard/', views.PartnerDashboardView.as_view(), name='partner-dashboard'),

    # Admin Config
    path('admin/config/', views.PlatformConfigView.as_view(), name='platform-config'),
]
