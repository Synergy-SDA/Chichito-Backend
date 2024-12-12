from django.apps import AppConfig

# apps.py
from django.apps import AppConfig

class YourAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cart'

    def ready(self):
        import cart.signal # Ensure signals are loaded
