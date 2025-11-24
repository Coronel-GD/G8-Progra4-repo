import json

from django.urls import reverse
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Item, OrderItem, Order, Payment, Category

# =========================
# HELPERS
# =========================
def get_active_order(user):
    try:
        return Order.objects.get(user=user, ordered=False)
    except Order.DoesNotExist:
        return None

# =========================
# HOME / PRODUCT
# =========================
class HomeView(View):
    def get(self, request, *args, **kwargs):
        category_slug = request.GET.get('category')
        
        if category_slug:
            items = Item.objects.filter(category__slug=category_slug)
        else:
            items = Item.objects.all()
        
        categories = Category.objects.filter(is_active=True)
        
        return render(request, 'home.html', {
            'object_list': items,
            'categories': categories
        })


class LoginView(View):
    def get(self, request, *args, **kwargs):
        # Si ya está autenticado, redirigir al home
        if request.user.is_authenticated:
            return redirect('core:home')
        return render(request, 'account/login.html')


class ProductDetailView(View):
    def get(self, request, slug, *args, **kwargs):
        item = get_object_or_404(Item, slug=slug)
        return render(request, 'product.html', {'object': item})


# =========================
# CART
# =========================
class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        order = get_active_order(request.user)
        return render(request, 'order_summary.html', {'order': order})

# =========================
# PAYMENT (MercadoPago)
# =========================
class PaymentView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        order = get_active_order(request.user)
        if not order or order.items.count() == 0:
            messages.error(request, "No tenés un pedido activo.")
            return redirect('core:order-summary')

        try:
            from .services import MercadoPagoService
            service = MercadoPagoService()
            payer_email = request.user.email or "test_user@test.com"
            
            payment_data = service.create_preference(order, payer_email)
            
            # Registrar Payment localmente
            payment = Payment.objects.create(
                mercadopago_id=payment_data["preference_id"],
                user=request.user,
                amount=payment_data["amount"],
            )
            order.payment = payment
            order.save()

            return redirect(payment_data["init_point"])

        except Exception as e:
            messages.error(request, f"Error procesando el pago: {str(e)}")
            return redirect('core:order-summary')

# =========================
# WEBHOOK
# =========================
class MercadoPagoWebhookView(View):
    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            from .services import MercadoPagoService
            service = MercadoPagoService()

            payment_id = data.get('data', {}).get('id') or data.get('id')
            if not payment_id:
                return JsonResponse({"error": "Missing payment id"}, status=400)

            info = service.get_payment_info(payment_id)
            payment = Payment.objects.filter(mercadopago_id=str(payment_id)).first()

            if not payment:
                return JsonResponse({"error": "Payment not found"}, status=404)

            if info.get("status") == "approved":
                payment.amount = info.get("transaction_amount", payment.amount)
                payment.save()

                order = Order.objects.filter(payment=payment).first()
                if order:
                    order.ordered = True
                    order.ordered_date = timezone.now()
                    order.save()

            return JsonResponse({"status": "ok"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

# =========================
# RESULT VIEWS
# =========================
class PaymentSuccessView(View):
    def get(self, request, *args, **kwargs):
        messages.success(request, "Pago aprobado, gracias por tu compra.")
        return redirect('core:order-summary')

class PaymentPendingView(View):
    def get(self, request, *args, **kwargs):
        messages.warning(request, "Pago pendiente.")
        return redirect('core:order-summary')

class PaymentFailureView(View):
    def get(self, request, *args, **kwargs):
        messages.error(request, "Pago rechazado.")
        return redirect('core:order-summary')

# =========================
# ADD / REMOVE CART
# =========================
@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, _ = OrderItem.objects.get_or_create(item=item, user=request.user, ordered=False)
    order = Order.objects.filter(user=request.user, ordered=False).first()

    if order:
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
        else:
            order.items.add(order_item)
    else:
        order = Order.objects.create(user=request.user)
        order.items.add(order_item)

    messages.success(request, "Producto agregado.")
    return redirect('core:order-summary')

@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order = Order.objects.filter(user=request.user, ordered=False).first()

    if order and order.items.filter(item__slug=item.slug).exists():
        oi = OrderItem.objects.filter(item=item, user=request.user, ordered=False).first()
        order.items.remove(oi)
        oi.delete()
        messages.info(request, "Producto eliminado.")
    else:
        messages.warning(request, "No está en el carrito.")

    return redirect('core:order-summary')

@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order = Order.objects.filter(user=request.user, ordered=False).first()

    if order and order.items.filter(item__slug=item.slug).exists():
        oi = OrderItem.objects.filter(item=item, user=request.user, ordered=False).first()
        if oi.quantity > 1:
            oi.quantity -= 1
            oi.save()
        else:
            order.items.remove(oi)
            oi.delete()
        messages.info(request, "Carrito actualizado.")
    else:
        messages.warning(request, "No está en el carrito.")

    return redirect('core:order-summary')
