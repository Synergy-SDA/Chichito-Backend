from django.urls import path
from .views import CategoryListCreateAPIView, CategoryDetailAPIView

urlpatterns = [
    path('categories/', CategoryListCreateAPIView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryDetailAPIView.as_view(), name='category-detail'),
]
