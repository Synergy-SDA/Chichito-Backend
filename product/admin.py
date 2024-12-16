from django.contrib import admin
from .models import Product, Feature, FeatureValue, ProductImage, FavoritProduct


class FeatureValueInline(admin.TabularInline):
    model = FeatureValue
    extra = 1  



@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('id','name',)  
    search_fields = ('id','name',)
    inlines = [FeatureValueInline]  



@admin.register(FeatureValue)
class FeatureValueAdmin(admin.ModelAdmin):
    list_display = ('id','feature', 'value')  
    search_fields = ('id','value', 'feature__name')  



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'price',
        'count_exist',
        'is_available',
        'created_at',
        'updated_at',
    )  
    list_filter = ('is_available', 'category', 'features')  
    search_fields = ('name', 'description', 'category__name')  
    readonly_fields = ('created_at', 'updated_at')  
    list_editable = ('price', 'count_exist', 'is_available')  
    ordering = ('-created_at',)  
    filter_horizontal = ('features',)  

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category', 'price', 'product_image')
        }),
        ('Inventory', {
            'fields': ('count_exist', 'is_available')
        }),
        ('Features', {
            'fields': ('features',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )  


    def save_model(self, request, obj, form, change):
        if obj.count_exist == 0:
            obj.is_available = False
        super().save_model(request, obj, form, change)



@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id','product',  'is_primary', 'created_at')
    list_filter = ('is_primary', 'created_at', 'product')
    search_fields = ('product__name',)
    list_editable = ('is_primary',)
    readonly_fields = ('created_at',)
    ordering = ('-is_primary', '-created_at')





@admin.register(FavoritProduct)
class FavoritProductAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'product', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'product__name')
    readonly_fields = ('added_at',)
    ordering = ('-added_at',)
