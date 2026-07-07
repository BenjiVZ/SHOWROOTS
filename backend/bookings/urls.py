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
    # Partner de producción (onboarding)
    path('partner/production/', views.PartnerProductionProfileView.as_view(), name='partner-production'),
    path('partner/production/submit/', views.PartnerProductionSubmitView.as_view(), name='partner-production-submit'),
    path('partner/production/photos/', views.PartnerProductionPhotosView.as_view(), name='partner-production-photos'),
    path('partner/production/photos/<int:pk>/', views.PartnerProductionPhotoDeleteView.as_view(), name='partner-production-photo-delete'),
    path('admin/partner-production/', views.AdminPartnerProductionListView.as_view(), name='admin-partner-production-list'),
    path('admin/partner-production/<int:pk>/action/', views.AdminPartnerProductionActionView.as_view(), name='admin-partner-production-action'),

    # Production Packs CRUD (Fase 5)
    path('partner/production/packs/', views.MyProductionPackListCreateView.as_view(), name='my-production-packs'),
    path('partner/production/packs/<int:pk>/', views.MyProductionPackDetailView.as_view(), name='my-production-pack-detail'),

    # Catálogo público (Fase 6)
    path('production-packs/', views.PublicProductionPackCatalogView.as_view(), name='production-packs-catalog'),
    path('production-packs/<int:pk>/', views.PublicProductionPackDetailView.as_view(), name='production-pack-detail'),

    # Booking ↔ Packs (Fase 7)
    path('bookings/<int:booking_id>/packs/', views.BookingPacksView.as_view(), name='booking-packs'),
    path('bookings/<int:booking_id>/packs/<int:pk>/', views.BookingPackRemoveView.as_view(), name='booking-pack-remove'),

    # Perfil dual (Fase 8)
    path('users/<int:user_id>/production-packs/', views.PartnerPublicPacksView.as_view(), name='user-production-packs'),

    # Perfil público del Aliado de producción
    path('aliado/<int:user_id>/', views.PartnerPublicProfileView.as_view(), name='partner-public-profile'),

    # Bundles (Fase 10)
    path('partner/production/bundles/', views.MyPackBundleListCreateView.as_view(), name='my-bundles'),
    path('partner/production/bundles/<int:pk>/', views.MyPackBundleDetailView.as_view(), name='my-bundle-detail'),
    path('production-bundles/', views.PublicPackBundleCatalogView.as_view(), name='production-bundles-catalog'),
    path('bookings/<int:booking_id>/bundles/', views.AddBundleToBookingView.as_view(), name='booking-add-bundle'),

    # Admin Config
    path('admin/config/', views.PlatformConfigView.as_view(), name='platform-config'),

    # Solicitudes abiertas ("Uber para DJs")
    path('open-gigs/',                            views.OpenGigRequestListCreateView.as_view(), name='open-gigs-list-create'),
    path('open-gigs/available/',                  views.OpenGigFeedView.as_view(),              name='open-gigs-available'),
    path('open-gigs/available-for-partner/',      views.OpenGigPartnerFeedView.as_view(),       name='open-gigs-available-partner'),
    path('open-gigs/<int:pk>/',                   views.OpenGigRequestDetailView.as_view(),     name='open-gigs-detail'),
    path('open-gigs/<int:pk>/cancel/',            views.OpenGigCancelView.as_view(),            name='open-gigs-cancel'),
    path('open-gigs/<int:pk>/offers/',            views.GigOfferCreateView.as_view(),           name='open-gigs-offer-create'),
    path('open-gigs/<int:gig_pk>/offers/<int:offer_pk>/accept/',
         views.GigOfferAcceptView.as_view(), name='open-gigs-offer-accept'),
    path('open-gigs/<int:gig_pk>/offers/<int:offer_pk>/reject/',
         views.GigOfferRejectView.as_view(), name='open-gigs-offer-reject'),
]
