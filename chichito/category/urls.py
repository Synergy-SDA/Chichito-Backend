from django.urls import path , re_path
from .views import *
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import CategoryAPIView

schema_view = get_schema_view(
    openapi.Info(
        title="User API",
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
    path('categories/', CategoryAPIView.as_view(), name='category-list-create'),  
    path('categories/<int:pk>/', CategoryAPIView.as_view(), name='category-detail'), 
]