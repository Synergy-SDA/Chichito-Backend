from django.urls import path , re_path
from .views import *
from rest_framework import permissions
# from .views import CategoryAPIView
from .views import CategoryViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'categories', CategoryViewSet , basename='category')

urlpatterns = [
    
]

urlpatterns += router.urls
