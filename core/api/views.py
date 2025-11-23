from rest_framework.generics import ListAPIView, RetrieveAPIView, RetrieveUpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings

from core.models import Item, Order, OrderItem, Payment
from core.services import MercadoPagoService
from .serializers import ItemSerializer, UserSerializer, OrderSerializer

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
    callback_url = "http://127.0.0.1:8000/accounts/google/login/callback/"

class GitHubLogin(SocialLoginView):
    adapter_class = GitHubOAuth2Adapter
    client_class = OAuth2Client
    callback_url = "http://127.0.0.1:8000/accounts/github/login/callback/"

class ItemListView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

class ItemDetailView(RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    lookup_field = 'slug'

class UserDetailView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        slug = request.data.get('slug', None)
        if not slug:
            return Response({"message": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

        item = get_object_or_404(Item, slug=slug)
        order_item, created = OrderItem.objects.get_or_create(
            item=item,
            user=request.user,
            ordered=False
        )
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            # check if the order item is in the order
            if order.items.filter(item__slug=item.slug).exists():
                order_item.quantity += 1
                order_item.save()
                return Response({"message": "Cantidad actualizada"}, status=status.HTTP_200_OK)
            else:
                order.items.add(order_item)
                return Response({"message": "Item agregado al carrito"}, status=status.HTTP_200_OK)
        else:
            ordered_date = timezone.now()
            order = Order.objects.create(user=request.user, ordered_date=ordered_date)
            order.items.add(order_item)
            return Response({"message": "Item agregado al carrito"}, status=status.HTTP_200_OK)

class OrderDetailView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            return order
        except Order.DoesNotExist:
            return None

class PaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        order = Order.objects.filter(user=request.user, ordered=False).first()
        if not order:
            return Response({"message": "No tienes una orden activa"}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            service = MercadoPagoService()
            # Usar el email del usuario o uno de prueba si no tiene
            payer_email = request.user.email or "test_user@test.com"
            
            payment_data = service.create_preference(order, payer_email)
            
            # Crear objeto Payment local
            payment = Payment.objects.create(
                mercadopago_id=payment_data["preference_id"],
                user=request.user,
                amount=payment_data["amount"]
            )
            order.payment = payment
            order.save()

            return Response(payment_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
