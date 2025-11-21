from django.urls import path
from .views import (
    HomeView,
    ProductDetailView,
    OrderSummaryView,
    add_to_cart,
    remove_from_cart,
    remove_single_item_from_cart,
    PaymentView,
    PaymentSuccessView,
    PaymentPendingView,
    PaymentFailureView,
    MercadoPagoWebhookView,
)

app_name = "core"

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('product/<slug>/', ProductDetailView.as_view(), name='product'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),

    # Carrito
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart, name='remove-single-item-from-cart'),

    # Pago Mercado Pago
    path('payment/', PaymentView.as_view(), name='payment'),

    # Resultados de pago
    path('payment/success/', PaymentSuccessView.as_view(), name='payment-success'),
    path('payment/pending/', PaymentPendingView.as_view(), name='payment-pending'),
    path('payment/failure/', PaymentFailureView.as_view(), name='payment-failure'),

    # Webhook Mercado Pago
    path('mercadopago/webhook/', MercadoPagoWebhookView.as_view(), name='mp-webhook'),
]
