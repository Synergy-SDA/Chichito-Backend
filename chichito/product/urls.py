from django.urls import path,re_path
from .views import *
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import ProductListView , ProductViewSet , FeatureViewSet , FeatureValueViewSet , ProductFilter
from rest_framework.routers import DefaultRouter



schema_view = get_schema_view(
    openapi.Info(
        title="Product API",
        default_version='v1',
        description="API documentation for user login and authentication",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="your_email@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


router = DefaultRouter()
router.register(r'Product', ProductViewSet, basename='product')
router.register(r'Feature', FeatureViewSet, basename='feature')
router.register(r'FeatureValue', FeatureValueViewSet, basename='feature-value')
router.register(r'ProductList', ProductListView, basename='product-list')
router.register(r'Filter', ProductFilter, basename='Filter')
router.register(r'sortByMinPrice' , ProductSortMinViewSet , basename='sort-by-min-price')
router.register(r'sortByMaxPrice' , ProductSortMaxViewSet , basename='sort-by-max-price')
router.register(r'sortByName' , ProductSortByNameViewSet , basename='sort-by-name')



urlpatterns = [
]

urlpatterns += router.urls
