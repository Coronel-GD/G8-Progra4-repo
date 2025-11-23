import mercadopago
from django.conf import settings
from django.urls import reverse

class MercadoPagoService:
    def __init__(self):
        self.access_token = getattr(settings, 'MERCADOPAGO_ACCESS_TOKEN', None)
        if not self.access_token:
            raise ValueError("MERCADOPAGO_ACCESS_TOKEN no está configurado en settings.")
        self.sdk = mercadopago.SDK(self.access_token)
        self.sandbox = bool(getattr(settings, 'MERCADOPAGO_SANDBOX', False))
        self.site_url = getattr(settings, "SITE_URL", "http://127.0.0.1:8000")

    def create_preference(self, order, payer_email):
        """
        Crea una preferencia de pago en MercadoPago y devuelve el punto de inicio (URL)
        y el ID de la preferencia.
        """
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
            raise ValueError("No hay productos en el pedido.")

        # Asegurar que SITE_URL no tenga slash al final para evitar doble slash
        site_url = self.site_url.rstrip('/')
        
        back_urls = {
            "success": f"{site_url}{reverse('core:payment-success')}",
            "failure": f"{site_url}{reverse('core:payment-failure')}",
            "pending": f"{site_url}{reverse('core:payment-pending')}",
        }

        preference_data = {
            "items": items,
            "payer": {"email": payer_email},
            "back_urls": back_urls,
            # "auto_return": "approved",  # Deshabilitado temporalmente para depuración
        }

        preference_response = self.sdk.preference().create(preference_data)
        response = preference_response.get("response")

        if not response:
            raise Exception("Mercado Pago no devolvió respuesta al crear la preferencia.")

        init_point = response.get("sandbox_init_point") if self.sandbox else response.get("init_point")
        
        if not init_point:
             # Fallback o error específico si no hay init_point
             error_msg = response.get("message") or "No se encontró la URL de inicio de pago (init_point)."
             raise Exception(f"Error de MercadoPago: {error_msg}")

        return {
            "preference_id": str(response.get("id", "")),
            "init_point": init_point,
            "amount": order.get_total() or 0.0
        }

    def get_payment_info(self, payment_id):
        """
        Obtiene la información de un pago desde MercadoPago dado su ID.
        """
        payment_response = self.sdk.payment().get(payment_id)
        return payment_response.get("response", {})
