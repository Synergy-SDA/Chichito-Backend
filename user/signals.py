from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import User, Wallet

@receiver(post_save, sender=User)
def create_wallet_for_new_user(sender, instance, created, **kwargs):
    # Check if the user is newly created (not just updated)
    if created:
        # Create a wallet for the newly created user
        Wallet.objects.create(user=instance)