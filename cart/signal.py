# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver

from user.models import User
# from django.contrib.auth.models import User
from .models import Cart

@receiver(post_save, sender=User)
def create_shopping_cart(sender, instance, created, **kwargs):
    if created:  # Only create a cart for newly registered users
        Cart.objects.create(user=instance)
