from django.db import transaction
from django.core.exceptions import ValidationError

class FavoritService:
    def __init__(self, user):
        self.user = user
    
    def add_to_favorites(self, product):
        from product.models import FavoritProduct

        if self._is_favorite(product):
            raise ValidationError("Product is already in favorites")
        
        with transaction.atomic():
            favorite = FavoritProduct.objects.create(
                user = self.user,
                product=product
            )
        return favorite
    
    def remove_from_favorites(self, product):

        from product.models import FavoritProduct

        try:
            favorite = FavoritProduct.objects.get(
                user = self.user,
                product = product
            )
            favorite.delete()
            return True
        except FavoritProduct.DoesNotExist:
            return False
    
    def get_favorites(self, queryset=None):

        from product.models import FavoritProduct

        favorites = FavoritProduct.objects.filter(user=self.user)

        if queryset is not None:
            favorites = favorites.filter(product__in = queryset)

        return favorites.select_related('product')

    def _is_favorite(self, product):

        from product.models import FavoritProduct

        return FavoritProduct.objects.filter(
            user=self.user,
            product=product
        ).exists()

    def toggle_favorite(self, product):

        if self._is_favorite(product):
            self.remove_from_favorites(product)
            return False
        else:
            self.add_to_favorites(product)
            return True
        
    
    