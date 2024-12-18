from rest_framework import serializers
from product.models import Product
from .models import CartItem
from .models import Cart,GiftWrap
from product.serializers import ProductImageSerializer
class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_price = serializers.DecimalField(source="product.price", max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.SerializerMethodField()
    images = ProductImageSerializer(source="product.images", many=True, read_only=True)
    gift_wrap_id = serializers.IntegerField(source="gift_wrap.id", read_only=True)
    gift_wrap_message = serializers.CharField(read_only=True)

    class Meta:
        model = CartItem
        fields = [
            'id', 
            'product', 
            'product_name', 
            'product_price', 
            'quantity', 
            'total_price', 
            'images',
            'gift_wrap_id',
            'gift_wrap_message',
        ]

    def get_total_price(self, obj):
        return obj.total_price()


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_price']

    def get_total_price(self, obj):
        return sum(item.total_price() for item in obj.items.all())


class GiftWrapSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiftWrap
        fields = ['id', 'name', 'price','giftwrap_image']






