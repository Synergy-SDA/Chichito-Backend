from django.db import models
from category.models import Category


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    count_exist = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    features = models.ManyToManyField(
        'FeatureValue',
        related_name='products'
    )
    category = models.ForeignKey(
        'category.Category',
        related_name='products',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.count_exist == 0:
            self.is_available = False
        super(Product, self).save(*args, **kwargs)
class Feature(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) :
        return self.name

class FeatureValue(models.Model):
    feature = models.ForeignKey(Feature, related_name='values', on_delete=models.CASCADE)
    value = models.CharField(max_length=255)  

    def __str__(self):
        return f'{self.feature.name}: {self.value}'



