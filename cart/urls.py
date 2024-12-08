from django.urls import path
from .views import CartAPIView,GiftWrapAPIView

urlpatterns = [
    path('cart/', CartAPIView.as_view(), name='cart'),

    path('gift-wrap/', GiftWrapAPIView.as_view(), name='gift-wrap-create'),
    path('gift-wrap/<int:pk>/', GiftWrapAPIView.as_view(), name='gift-wrap-retrieve-update-delete'),
]
