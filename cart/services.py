from .models import Cart, CartItem
from product.models import Product
from django.core.exceptions import ValidationError


class CartService:
    @staticmethod
    def get_or_create_cart(user):
        cart, created = Cart.objects.get_or_create(user=user)
        return cart

    @staticmethod
    def add_item(cart, product_id, quantity):
        print(product_id)
        product = Product.objects.filter(id=product_id, is_available=True).first()
        
        if not product:
            raise ValidationError("Product not available.")
        if quantity > product.count_exist:
            raise ValidationError("Not enough stock available.")

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
        cart_item.save()
        return cart_item

    @staticmethod
    def update_item(cart, product_id, quantity):
        cart_item = CartItem.objects.filter(cart=cart, product_id=product_id).first()
        if not cart_item:
            raise ValidationError("Item not in cart.")
        if quantity > cart_item.product.count_exist:
            raise ValidationError("Not enough stock available.")
        cart_item.quantity = quantity
        cart_item.save()
        return cart_item

    @staticmethod
    def remove_item(cart, product_id):
        cart_item = CartItem.objects.filter(cart=cart, product_id=product_id).first()
        if cart_item:
            cart_item.delete()
