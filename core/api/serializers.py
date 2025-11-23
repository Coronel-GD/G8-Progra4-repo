from rest_framework import serializers
from rest_framework import serializers
from django.contrib.auth import get_user_model
from core.models import Item, UserProfile, Order, OrderItem

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (

            'one_click_purchasing',
            'street_address',
            'apartment_address',
            'zip_code',
            'city',
            'country',
        )

class UserSerializer(serializers.ModelSerializer):
    userprofile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'userprofile')
        read_only_fields = ('email',)
        extra_kwargs = {'username': {'required': False}}

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('userprofile', {})
        profile = instance.userprofile

        instance.username = validated_data.get('username', instance.username)
        instance.save()

        profile.street_address = profile_data.get('street_address', profile.street_address)
        profile.apartment_address = profile_data.get('apartment_address', profile.apartment_address)
        profile.zip_code = profile_data.get('zip_code', profile.zip_code)
        profile.city = profile_data.get('city', profile.city)
        profile.country = profile_data.get('country', profile.country)
        profile.save()

        return instance

class ItemSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    label_display = serializers.CharField(source='get_label_display', read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = (
            'id',
            'title',
            'price',
            'discount_price',
            'category',
            'category_display',
            'label',
            'label_display',
            'slug',
            'description',
            'image_url',
        )

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

class OrderItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer()
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = (
            'id',
            'item',
            'quantity',
            'final_price',
        )

    def get_final_price(self, obj):
        return obj.get_final_price()

class OrderSerializer(serializers.ModelSerializer):
    order_items = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id',
            'order_items',
            'total',
            'ordered',
            'ordered_date',
        )

    def get_order_items(self, obj):
        return OrderItemSerializer(obj.items.all(), many=True).data

    def get_total(self, obj):
        return obj.get_total()
