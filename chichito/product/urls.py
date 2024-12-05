from django.urls import path,re_path
from .views import *
from rest_framework import permissions
from .views import ProductListView , ProductViewSet , FeatureViewSet , FeatureValueViewSet , ProductFilter
from rest_framework.routers import DefaultRouter




router = DefaultRouter()
router.register(r'Product', ProductViewSet, basename='product')
router.register(r'Feature', FeatureViewSet, basename='feature')
router.register(r'FeatureValue', FeatureValueViewSet, basename='feature-value')
router.register(r'ProductList', ProductListView, basename='product-list')
router.register(r'Filter', ProductFilter, basename='Filter')
router.register(r'sortByMinPrice' , ProductSortMinViewSet , basename='sort-by-min-price')
router.register(r'sortByMaxPrice' , ProductSortMaxViewSet , basename='sort-by-max-price')
router.register(r'sortByName' , ProductSortByNameViewSet , basename='sort-by-name')
router.register(r'search', ProductSearchViewSet, basename='product-search')



urlpatterns = [
]

urlpatterns += router.urls
