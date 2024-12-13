from django.urls import path
from .views import *

urlpatterns = [
    path('cart/', CartAPIView.as_view(), name='cart'),
    path('cart/<int:cart_id>/',CartRetriveAPI.as_view(), name='cart-delete'),
    path('cart/all/',CartRetriveALLAPI.as_view(), name='cart-get-all'),
    path('cart/delete/<int:cart_id>/',CartDeleteAPI.as_view(), name='cart-delete'),

    path('gift-wrap/', GiftWrapAPIView.as_view(), name='gift-wrap-create'),
    path('gift-wrap/<int:pk>/', GiftWrapAPIView.as_view(), name='gift-wrap-retrieve-update-delete'),

    path('gift-wrap-retrive/', GiftWrapRetriveAPI.as_view(), name='gift-wrap-retrive'),

    
]
