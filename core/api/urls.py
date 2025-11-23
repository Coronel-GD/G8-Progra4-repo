from django.urls import path
from .views import (
    ItemListView, 
    ItemDetailView, 
    UserDetailView, 
    AddToCartView, 
    OrderDetailView, 
    PaymentAPIView,
    GoogleLogin,
    GitHubLogin
)

urlpatterns = [
    path('auth/google/', GoogleLogin.as_view(), name='google_login'),
    path('auth/github/', GitHubLogin.as_view(), name='github_login'),
    path('products/', ItemListView.as_view(), name='product-list'),
    path('products/<slug>/', ItemDetailView.as_view(), name='product-detail'),
    path('user/', UserDetailView.as_view(), name='user-detail'),
    path('add-to-cart/', AddToCartView.as_view(), name='add-to-cart'),
    path('order-summary/', OrderDetailView.as_view(), name='order-summary'),
    path('checkout/', PaymentAPIView.as_view(), name='checkout'),
]
