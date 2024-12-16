from django.db import models
from user.models import User
from product.models import Product
from cart.models import Cart, CartItem


class Order(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'

    payment_status = models.CharField(
            max_length=20,
            choices=PaymentStatus.choices,
            default=PaymentStatus.PENDING
    )
    payment_date = models.DateTimeField(null=True, blank=True)
    class StatusChoices(models.TextChoices): 
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        SHIPPED = 'SHIPPED', 'Shipped'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELED = 'CANCELED', 'Canceled'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True, related_name="order")
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,  
        default=StatusChoices.PENDING
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_total_price(self):
        print("vvv")
        self.total_price = sum(item.total_price() for item in self.items.all())
        self.save()

    def __str__(self):
        return f"Order {self.id} - {self.user.username} - {self.status}"



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    gift_wrap = models.ForeignKey('cart.GiftWrap', on_delete=models.SET_NULL, blank=True, null=True)
    gift_wrap_message = models.TextField(blank=True, null=True)

    def total_price(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order {self.order.id})"
