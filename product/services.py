from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Product
from django.db.models.functions import Coalesce 
from django.db.models import Sum, Value, F
from Order.models import Order
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
        
class ProductService:
    @staticmethod
    def get_most_sold_products(limit=8):
        try:
            # Annotating sold_count based on the quantity of order items for each product
            sold_products = (
                Product.objects
                .annotate(
                    sold_count=Coalesce(
                        Sum('orderitem__quantity', filter=F('orderitem__order__status') == Order.StatusChoices.COMPLETED),
                        Value(0)
                    )
                )
                .order_by('-sold_count')[:limit]  # Get the top 'limit' sold products
            )

            # Debugging print to see the result of the query
            print(f"Sold Products: {sold_products}")
            
            # If fewer than `limit` products are sold, add unsold products
            if sold_products.count() < limit:
                # Getting additional products to make up for the missing count
                additional_products = (
                    Product.objects
                    .exclude(id__in=[product.id for product in sold_products])
                    .annotate(
                        sold_count=Value(0)
                    )
                    .order_by('id')[: limit - sold_products.count()]
                )
                sold_products = list(sold_products) + list(additional_products)

            return sold_products

        except Exception as e:
            # Print exception details to help debug the issue
            print(f"Error occurred: {str(e)}")
            return []
