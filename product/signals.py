from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Product


def clear_cache_for_product(instance):
    """
    Clear related caches for a product instance
    """
    # Delete list cache
    cache.delete_pattern('product_list*')  

    
    detail_key = f'product_detail_{instance.id}'
    cache.delete(detail_key)


@receiver(post_save, sender=Product)
def handle_product_update(sender, instance, created, **kwargs):
    clear_cache_for_product(instance)


@receiver(post_delete, sender=Product)
def handle_product_delete(sender, instance, **kwargs):
    clear_cache_for_product(instance)
