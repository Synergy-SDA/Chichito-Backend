from django.urls import path
from .views import *

urlpatterns = [
    # path('products/', ProductAPIView.as_view(), name='product-list-create'),  
    # path('products/<int:pk>/', ProductAPIView.as_view(), name='product-retrieve-update-delete'),
    path('features/', FeatureAPIView.as_view(), name='feature-list-create'), 
    path('features/<int:pk>/', FeatureAPIView.as_view(), name='feature-retrieve-update-delete'),  
    path('feature-values/', FeatureValueAPIView.as_view(), name='feature-value-list-create'), 
    path('feature-values/<int:pk>/', FeatureValueAPIView.as_view(), name='feature-value-retrieve-update-delete'),  
]