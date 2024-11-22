from django.urls import path,re_path
from .views import *
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


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

urlpatterns = [
    path('products/', ProductAPIView.as_view(), name='product-list-create'),  
    path('products/<int:pk>/', ProductAPIView.as_view(), name='product-retrieve-update-delete'),
    path('features/', FeatureAPIView.as_view(), name='feature-list-create'), 
    path('features/<int:pk>/', FeatureAPIView.as_view(), name='feature-retrieve-update-delete'),  
    path('feature-values/', FeatureValueAPIView.as_view(), name='feature-value-list-create'), 
    path('feature-values/<int:pk>/', FeatureValueAPIView.as_view(), name='feature-value-retrieve-update-delete'),
    path('products/<str:category_name>/', ProductPerCategoryAPIView.as_view(), name='products-per-category'),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
] 

