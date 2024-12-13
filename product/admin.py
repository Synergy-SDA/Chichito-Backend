from django.contrib import admin
from .models import Product,ProductImage,Feature,FeatureValue

admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Feature)
admin.site.register(FeatureValue)