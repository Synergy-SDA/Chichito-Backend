from django.db import models
from category.models import Category
from user.models import *
from django.utils.translation import gettext_lazy as _
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    count_exist = models.IntegerField(default=0)
    product_image = models.ImageField(upload_to='product_images/', null=True, blank=True)
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



class Comment(models.Model):
    user = models.ForeignKey(
        User, related_name='comments', on_delete=models.CASCADE
    )  
    product = models.ForeignKey(
        Product, related_name='comments', on_delete=models.CASCADE
    )  
    content = models.CharField(max_length=255)
    
    class RatingChoices(models.IntegerChoices):
        ONE = 1, 'One Star'
        TWO = 2, 'Two Stars'
        THREE = 3, 'Three Stars'
        FOUR = 4, 'Four Stars'
        FIVE = 5, 'Five Stars'
    
    rate = models.IntegerField(choices=RatingChoices.choices)

    def __str__(self):
        return f"{self.user.email} - {self.content[:20]}"  

class ProductImage(models.Model):
    product = models.ForeignKey(
        'Product',
        related_name='images',
        on_delete=models.CASCADE,
        verbose_name=_('Product')
        )
    image = models.ImageField(
        upload_to='product_images',
        verbose_name=_('Product Image'),
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name=_('Primary Image')
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meat:
        verbose_name = _('Product Image')
        verbose_name_plural = _('Product Images')
        ordering = ['-is_primary', '-created_at']
    
    def __str__(self):
        return f"Image for {self.product.name} ({'Primary' if self.is_primary else 'Secondary'})"
    
    def save(self, *args, **kwargs):
        # This method ensures that for a given product,
        # only one image can be marked as the primary image (is_primary=True). 
        # If a new image is set as the primary image, any previously marked primary image is updated 
        # to is_primary=False
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product,
                is_primary=True
            ).update(is_primary=False)
        super().save(*args, **kwargs)
