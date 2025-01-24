from urllib import response

from .models import Cart, CartItem, GiftWrap
from product.models import Product
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import serializers


class CartService:
    @staticmethod
    def get_or_create_cart(user):
        cart, created = Cart.objects.get_or_create(user=user)
        return cart
    
    @staticmethod
    def get_user_cartitem(cart_id):
        return CartItem.objects.filter(id=cart_id).first()

    @staticmethod
    def add_item(cart, product_id, quantity, gift_wrap_id=None, gift_wrap_message=None):
        try:
            # print(product_id)
            product = Product.objects.filter(id=product_id, is_available=True).first()
            if not product:
                raise serializers.ValidationError({"error": "Product not available."})
            
            if quantity > product.count_exist:
                raise ValidationError({"error": "Not enough stock available."})

            gift_wrap = None
            if gift_wrap_id:
                gift_wrap = GiftWrap.objects.filter(id=gift_wrap_id).first()
                if not gift_wrap:
                    raise ValidationError({"error": "Invalid gift wrap selected."})

            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            if quantity:
                cart_item.quantity += quantity
    
            cart_item.gift_wrap = gift_wrap
            cart_item.gift_wrap_message = gift_wrap_message
            print(created)
            cart_item.save()
            return cart_item
        except Exception as e:    
            raise e
            


    @staticmethod
    def update_item(cart, product_id, quantity, gift_wrap_id=None, gift_wrap_message=None):
        # print("va")
        # print(cart)
        # print(product_id)
        cart_item = get_object_or_404(CartItem, cart=cart ,id = product_id)
        print(cart_item)
        if not cart_item:
            raise ValidationError("Item not in cart.")
        if quantity > cart_item.product.count_exist:
            raise ValidationError("Not enough stock available.")
        cart_item.quantity = quantity

        if gift_wrap_id:
            gift_wrap = GiftWrap.objects.filter(id=gift_wrap_id).first()
            if not gift_wrap:
                raise ValidationError("Invalid gift wrap selected.")
            cart_item.gift_wrap = gift_wrap

        if gift_wrap_message:
            cart_item.gift_wrap_message = gift_wrap_message

        # print("inja?")
        cart_item.save()
        # print("inja chi?")
        return cart_item

    @staticmethod
    def remove_item(cart):
        cart_item = CartItem.objects.filter(id=cart).first()
        if cart_item:
            cart_item.delete()
