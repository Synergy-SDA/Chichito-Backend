from django.apps import AppConfig


class OrderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Order'

    def ready(self):
        import Order.signals  # Import the signals module to register signal handlers
