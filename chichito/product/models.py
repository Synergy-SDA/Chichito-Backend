from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    count_exist = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.stock == 0:
            self.is_available = False
        super(Product, self).save(*args, **kwargs)

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey(
        'self',
        related_name='subcategories',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    

class Feature(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) :
        return self.name

class FeatureValue(models.Model):
    feature = models.ForeignKey(Feature, related_name='values', on_delete=models.CASCADE)
    value = models.CharField(max_length=255)  

    def __str__(self):
        return f'{self.feature.name}: {self.value}'

class ProductFeature(models.Model):
    product = models.ForeignKey(Product, related_name='product_features', on_delete=models.CASCADE)
    feature_value = models.ForeignKey(FeatureValue, related_name='product_features', on_delete=models.CASCADE)

    class Meta:
        unique_together = ['product', 'feature_value']

    def __str__(self):
        return f'{self.product.name} - {self.feature_value.feature.name}: {self.feature_value.value}'




