from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import User, Wallet
from cart.models import Cart  

@receiver(post_save, sender=User)
def create_wallet_for_new_user(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)
        