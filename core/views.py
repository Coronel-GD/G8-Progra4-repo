import json
import mercadopago
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

from .models import Item, OrderItem, Order, Payment

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
        items = Item.objects.all()
        return render(request, 'home.html', {'object_list': items})


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

        access_token = getattr(settings, 'MERCADOPAGO_ACCESS_TOKEN', None)
        if not access_token:
            messages.error(request, "Falta configurar MERCADOPAGO_ACCESS_TOKEN en settings.")
            return redirect('core:order-summary')
        mp = mercadopago.SDK(access_token)

        items = []
        for oi in order.items.all():
            qty = int(oi.quantity) if oi.quantity and oi.quantity > 0 else 1
            final = oi.get_final_price()
            unit_price = float(final / qty) if final else 0.0
            title = (oi.item.title or "Producto")[:120]
            currency = oi.item.currency or "ARS"
            items.append({
                "title": title,
                "quantity": qty,
                "unit_price": unit_price,
                "currency_id": currency,
            })

        if not items:
            messages.error(request, "No hay productos en el pedido.")
            return redirect('core:order-summary')

        payer_email = request.user.email or "test_user@test.com"
        site_url = getattr(settings, "SITE_URL", "http://127.0.0.1:8000")

        back_urls = {
            "success": f"{site_url}{reverse('core:payment-success')}",
            "failure": f"{site_url}{reverse('core:payment-failure')}",
            "pending": f"{site_url}{reverse('core:payment-pending')}",
        }
        print("Back URLs enviadas:", back_urls)  # <-- debug

        # En sandbox no usamos auto_return
        preference_data = {
            "items": items,
            "payer": {"email": payer_email},
            "back_urls": back_urls,
        }

        try:
            pref_resp = mp.preference().create(preference_data)
            response = pref_resp.get("response")
            print("Respuesta completa de MercadoPago:", response)

            if not response:
                messages.error(request, "Mercado Pago no devolvió respuesta al crear la preferencia.")
                return redirect('core:order-summary')

            sandbox = bool(getattr(settings, 'MERCADOPAGO_SANDBOX', False))
            init_point = response.get("sandbox_init_point") if sandbox else response.get("init_point")
            print("Init point elegido:", init_point)

            if not init_point:
                error_msg = response.get("message") or "No se encontró la URL de inicio de pago (init_point)."
                messages.error(request, f"Error de MercadoPago: {error_msg}")
                return redirect('core:order-summary')

            payment = Payment.objects.create(
                mercadopago_id=str(response.get("id", "")),
                user=request.user,
                amount=order.get_total() or 0.0,
            )
            order.payment = payment
            order.save()

            return redirect(init_point)

        except Exception as e:
            print("Excepción en PaymentView:", e)
            messages.error(request, f"Error creando preferencia: {str(e)}")
            return redirect('core:order-summary')

        # 4) Payer y back URLs
        payer_email = request.user.email or "test_user@test.com"
        site_url = getattr(settings, "SITE_URL", "http://127.0.0.1:8000")

        back_urls = {
            "success": f"{site_url}{reverse('core:payment-success')}/",
            "failure": f"{site_url}{reverse('core:payment-failure')}/",
            "pending": f"{site_url}{reverse('core:payment-pending')}/",
        }

        preference_data = {
            "items": items,
            "payer": {"email": payer_email},
            "back_urls": back_urls,
            "auto_return": "approved",
        }

        # 5) Crear preferencia
        try:
            pref_resp = mp.preference().create(preference_data)
            response = pref_resp.get("response")
            print("Respuesta completa de MercadoPago:", response)

            if not response:
                messages.error(request, "Mercado Pago no devolvió respuesta al crear la preferencia.")
                return redirect('core:order-summary')

            sandbox = bool(getattr(settings, 'MERCADOPAGO_SANDBOX', False))
            init_point = response.get("sandbox_init_point") if sandbox else response.get("init_point")
            print("Init point elegido:", init_point)

            if not init_point:
                error_msg = response.get("message") or "No se encontró la URL de inicio de pago (init_point)."
                messages.error(request, f"Error de MercadoPago: {error_msg}")
                return redirect('core:order-summary')

            # Registrar Payment
            payment = Payment.objects.create(
                mercadopago_id=str(response.get("id", "")),
                user=request.user,
                amount=order.get_total() or 0.0,
            )
            order.payment = payment
            order.save()

            return redirect(init_point)

        except Exception as e:
            print("Excepción en PaymentView:", e)
            messages.error(request, f"Error creando preferencia: {str(e)}")
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
            mp = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

            payment_id = data.get('data', {}).get('id') or data.get('id')
            if not payment_id:
                return JsonResponse({"error": "Missing payment id"}, status=400)

            info = mp.payment().get(payment_id).get("response", {})
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
