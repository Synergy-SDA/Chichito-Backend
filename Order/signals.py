from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order

@receiver(post_save, sender=Order)
def handle_order_status_update(sender, instance, **kwargs):
    if instance.payment_status == Order.PaymentStatus.COMPLETED:
        if instance.status == Order.StatusChoices.PENDING:
            instance.status = Order.StatusChoices.COMPLETED
            instance.save()
