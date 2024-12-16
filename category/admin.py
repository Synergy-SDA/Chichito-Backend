from django.contrib import admin
from .models import Category
# Register your models here.
from django.contrib import admin
from .models import Category

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'parent', 'description')  
    list_filter = ('parent',)  
    search_fields = ('name', 'description')  
    ordering = ('name',)  
    list_editable = ('description',)  


admin.site.register(Category, CategoryAdmin)

