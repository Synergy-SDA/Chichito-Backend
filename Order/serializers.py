from rest_framework import serializers
from django.db import transaction
from cart.services import CartService
from user.models import Wallet
from .models import Order, OrderItem
from rest_framework import serializers
from .models import Order, OrderItem
from cart.models import Cart
from django.utils.timezone import now
from product.serializers import ProductImageSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    images = ProductImageSerializer(source="product.images", many=True, read_only=True) 
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name','images', 'quantity', 'price', 'total_price']
        read_only_fields = ['id', 'price', 'total_price']



class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total_price', 'items', 'created_at', 'updated_at']
        read_only_fields = ['id', 'total_price', 'created_at', 'updated_at']


class CreateOrderSerializer(serializers.Serializer):
    """
    Serializer for creating an order from the user's shopping cart.
    """
    def validate(self, data):
        user = self.context['request'].user
        cart = Cart.objects.filter(user=user).last()  # Get the most recent cart

        if not cart:
            raise serializers.ValidationError("No shopping cart found for this user.")

        if not cart.items.exists():
            raise serializers.ValidationError("Your cart is empty.")

        return {'cart': cart}

    def create(self, validated_data):
        cart = validated_data.get('cart')
        if not cart:
            raise serializers.ValidationError("No valid cart found to create the order.")

        user = self.context['request'].user

        # Create the order
        print("kos")
        order = Order.objects.create(user=user, cart=cart)
        print("kir")

        # Move cart items to order items
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
                gift_wrap=item.gift_wrap,
                gift_wrap_message=item.gift_wrap_message
            )

        # Calculate the total price of the order
        order.calculate_total_price()

        # Clear the cart by removing all items (instead of deleting the cart)
        cart.items.all().delete()

        # After the order, create a new cart for the user (to ensure cart availability for next order)
        new_cart = Cart.objects.create(user=user)

        return order




class PaymentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()

    def validate_order_id(self, value):
        try:
            order = Order.objects.get(id=value)
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order does not exist.")

        if order.payment_status == Order.PaymentStatus.COMPLETED:
            raise serializers.ValidationError("This order has already been paid.")
        
        return value
    
    
        

    def process_payment(self, validated_data):
        order_id = validated_data['order_id']
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order does not exist.")

        if order.payment_status == Order.PaymentStatus.COMPLETED:
            raise serializers.ValidationError("This order has already been paid.")

        try:
            wallet = Wallet.objects.get(user=order.user)
        except Wallet.DoesNotExist:
            raise serializers.ValidationError("Wallet not found for the user.")

        with transaction.atomic():
            try:
                wallet.deduct_balance(order.total_price)
                order.payment_status = Order.PaymentStatus.COMPLETED
                order.status = order.StatusChoices.PROCESSING
                print(order.payment_status)
                order.payment_date = now()
                order.save()    
                return order
            except ValueError as e:
                order.payment_status = Order.PaymentStatus.FAILED
                order.save()
                raise serializers.ValidationError(str(e))






class AdminOrderStatusUpdateSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    new_status = serializers.ChoiceField(choices=[
        Order.StatusChoices.PENDING,
        Order.StatusChoices.PROCESSING,
        Order.StatusChoices.COMPLETED,
        Order.StatusChoices.CANCELED,
    ])

    def update_status(self, validated_data):
        order_id = validated_data['order_id']
        new_status = validated_data['new_status']

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found.")

        if order.status == new_status:
            raise serializers.ValidationError(f"The order is already in the status '{new_status}'.")

        order.status = new_status
        order.save()
        return {"message": f"Order status updated to '{new_status}'.", "order_id": order.id}




