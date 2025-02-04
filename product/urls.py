from django.urls import path
from .views import *
from .views import *






urlpatterns = [
    path('comments/' , CommentCreateAPI.as_view(), name='comment'),
    # path('comments/', CommentRetriveView.as_view() , name='comment-id'),
    path('comments/<int:comment_id>/', CommentRetriveView.as_view(), name='comment-detail'),
    path('AllComments/', ShowAllCommentView.as_view(), name='show_all_comments'),
    # path('comments/<int:pk>/', CommentUpdateAPI.as_view(), name='comment-update'),

    path('products/<int:product_id>/comments/', ProductCommentsView.as_view(), name='product-comments'),
    
    
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
    path('products/filter-and-sort/', ProductFilterAndSortAPIView.as_view(), name='product-filter-and-sort'),
    
    
    path('products/<int:product_id>/similar/', SimilarProductsView.as_view(), name='similar-products'),

    path('products/<int:product_pk>/images/<int:image_pk>/', 
         ProductImageDeleteView.as_view(), 
         name='product-image-delete'),
    path('products/<int:product_pk>/images/<int:image_pk>/set-primary/', 
         ProductImagePrimaryView.as_view(), 
         name='product-image-set-primary'),

    path('favorites/', FavoriteAPI.as_view(), name='favorite-list'),
    path('favorites/toggle/', FavoriteToggleAPIView.as_view(), name='favorite-toggle'),    

    path('products/most-sold/', MostSoldProductsView.as_view(), name='most-sold-products'),


]

