from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .models import Item, OrderItem, Order, Payment

# --- Resources para import/export ---

class ItemResource(resources.ModelResource):
    class Meta:
        model = Item
        import_id_fields = ['id']
        fields = ('id', 'title', 'price', 'discount_price', 'category', 'label', 'slug', 'description', 'currency')

class OrderResource(resources.ModelResource):
    class Meta:
        model = Order
        import_id_fields = ['id']
        fields = ('id', 'user', 'ordered', 'ordered_date')

# --- Admin ---

@admin.register(Item)
class ItemAdmin(ImportExportModelAdmin):
    resource_class = ItemResource
    list_display = ('title', 'price', 'discount_price', 'category', 'label')
    search_fields = ('title',)
    list_filter = ('category', 'label')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'quantity', 'ordered')
    list_filter = ('ordered',)
    search_fields = ('user__username', 'item__title')


@admin.register(Order)
class OrderAdmin(ImportExportModelAdmin):
    resource_class = OrderResource
    list_display = ('user', 'ordered', 'ordered_date')
    list_filter = ('ordered',)
    search_fields = ('user__username',)
    filter_horizontal = ('items',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('mercadopago_id', 'user', 'amount', 'timestamp')
    search_fields = ('mercadopago_id', 'user__username')
