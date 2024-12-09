from django.db import models
from product.models import Product  
from user.models import User
from django.utils.timezone import now


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    gift_wrap = models.ForeignKey('GiftWrap', on_delete=models.SET_NULL, blank=True, null=True)
    gift_wrap_message = models.TextField(blank=True, null=True)  # Message specific to the cart item
    created_at = models.DateTimeField(auto_now_add=True)
    def total_price(self):
        return self.quantity * self.product.price

    class Meta:
        unique_together = ('cart', 'product')

class GiftWrap(models.Model):
    name = models.CharField(max_length=100)  
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)  
    description = models.TextField(blank=True, null=True) 
    giftwrap_image = models.ImageField(upload_to='gift_wraps/', blank=True, null=True)  
    def __str__(self):
        return self.name
