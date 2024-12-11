from django.urls import path
from .views import *
from .views import *






urlpatterns = [
    path('comments/' , CommentCreateAPI.as_view(), name='comment'),
    path('comments/<int:product_id>/', CommentRetriveView.as_view() , name='comment-id'),
    path('products/', ProductListAPIView.as_view(), name='product-list'),
    path('product/<int:pk>/', ProductAPIView.as_view(), name='product-retrieve-update-delete'),
    
    path('features/', FeatureListAPIView.as_view(), name='feature-list'),
    path('feature/<int:pk>/', FeatureAPIView.as_view(), name='feature-detail'), 


    path('feature-values/', FeatureValueListAPIView.as_view(), name='feature-value-list'),  
    path('feature-value/<int:pk>/', FeatureValueAPIView.as_view(), name='feature-value-detail'), 

    path('products/category/<str:category_name>/', ProductPerCategoryAPIView.as_view(), name='products-per-category'),

    path('products/search/', ProductSearchAPIView.as_view(), name='product-search'),

    path('products/sort/', ProductSortByNameAPIView.as_view(), name='product-sort-by-name'),

    path('products/sort/price/', ProductSortPriceAPIView.as_view(), name='product-sort-by-price'),

    path('products/filter/', ProductFilterAPIView.as_view(), name='product-filter'),

    path('products/<int:product_pk>/images/<int:image_pk>/', 
         ProductImageDeleteView.as_view(), 
         name='product-image-delete'),
    path('products/<int:product_pk>/images/<int:image_pk>/set-primary/', 
         ProductImagePrimaryView.as_view(), 
         name='product-image-set-primary'),


]

