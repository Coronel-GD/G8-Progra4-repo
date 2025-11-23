from django.conf import settings
from django.contrib.gis.db import models
from django.shortcuts import reverse

class Category(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField()
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'


class Label(models.Model):
    title = models.CharField(max_length=50, verbose_name='Nombre')
    css_class = models.CharField(max_length=20, verbose_name='Clase CSS', help_text='ej: primary, secondary, danger, success')
    color = models.CharField(max_length=7, verbose_name='Color (Hex)', blank=True, null=True, help_text='ej: #FF5733')
    is_active = models.BooleanField(default=True, verbose_name='Activa')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Etiqueta'
        verbose_name_plural = 'Etiquetas'


class Item(models.Model):
    title = models.CharField(max_length=120, verbose_name='Título')
    price = models.FloatField(verbose_name='Precio')
    discount_price = models.FloatField(blank=True, null=True, verbose_name='Precio con descuento')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, verbose_name='Categoría')
    label = models.ForeignKey(Label, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Etiqueta')
    slug = models.SlugField(unique=True, verbose_name='Slug (URL amigable)')
    description = models.TextField(blank=True, verbose_name='Descripción')
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name='Imagen')
    currency = models.CharField(max_length=3, default='ARS', verbose_name='Moneda')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('core:product', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        if self.item.discount_price:
            return self.quantity * self.item.discount_price
        return self.get_total_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()

    class Meta:
        verbose_name = 'Item de Orden'
        verbose_name_plural = 'Items de Orden'


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(blank=True, null=True)
    ordered = models.BooleanField(default=False)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)
    shipping_cost = models.FloatField(default=0.0)

    def __str__(self):
        return f"Order {self.pk} - {self.user.username}"

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total + self.shipping_cost

    class Meta:
        verbose_name = 'Orden'
        verbose_name_plural = 'Ordenes'


class Payment(models.Model):
    mercadopago_id = models.CharField(max_length=128, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.pk} - {self.user.username if self.user else 'anon'}"

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)
    
    # Address Fields
    street_address = models.CharField(max_length=100, blank=True, null=True)
    apartment_address = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    location = models.PointField(blank=True, null=True)  # Coordenadas (longitud, latitud)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
