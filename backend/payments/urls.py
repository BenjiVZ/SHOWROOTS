from django.urls import path

from .views import (
    ConfirmCheckoutView,
    InitCheckoutView,
    PayoutListView,
    PayoutMarkPaidView,
    RefundView,
    StatusView,
    WebhookView,
)

urlpatterns = [
    # Frontend
    path('payments/paguelofacil/init/', InitCheckoutView.as_view(), name='pfl-init'),
    path('payments/paguelofacil/confirm/', ConfirmCheckoutView.as_view(), name='pfl-confirm'),
    path('payments/paguelofacil/status/<str:internal_reference>/', StatusView.as_view(), name='pfl-status'),

    # PFL → nosotros
    path('payments/paguelofacil/webhook/', WebhookView.as_view(), name='pfl-webhook'),

    # Admin
    path('payments/admin/payouts/', PayoutListView.as_view(), name='pfl-payouts'),
    path('payments/admin/payouts/<int:pk>/pay/', PayoutMarkPaidView.as_view(), name='pfl-payout-pay'),
    path('payments/admin/refund/<int:tx_id>/', RefundView.as_view(), name='pfl-refund'),
]
