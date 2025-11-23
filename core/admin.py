from django.contrib import admin
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .models import Item, OrderItem, Order, Payment, Category, Label

# --- Resources para import/export ---

class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category
        import_id_fields = ['id']
        fields = ('id', 'title', 'slug', 'description', 'is_active')

class LabelResource(resources.ModelResource):
    class Meta:
        model = Label
        import_id_fields = ['id']
        fields = ('id', 'title', 'css_class', 'color', 'is_active')

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

@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    resource_class = CategoryResource
    list_display = ('title', 'slug', 'is_active')
    search_fields = ('title',)
    prepopulated_fields = {"slug": ("title",)}

@admin.register(Label)
class LabelAdmin(ImportExportModelAdmin):
    resource_class = LabelResource
    list_display = ('title', 'css_class', 'color', 'is_active')
    search_fields = ('title',)
    list_filter = ('is_active',)

@admin.register(Item)
class ItemAdmin(ImportExportModelAdmin):
    resource_class = ItemResource
    list_display = ('title', 'price', 'discount_price', 'category', 'label', 'image_preview')
    search_fields = ('title',)
    list_filter = ('category', 'label')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height: auto;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Vista Previa'

    class Media:
        js = ('js/admin_image_preview.js',)


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
