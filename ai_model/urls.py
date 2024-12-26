from django.urls import include, path
from .views import UserInformationAPIView
from .views import ModelResultAPIView
urlpatterns = [
    path('suggest/user_data', UserInformationAPIView.as_view(),name = 'user_data'),
    path('suggest/predictions', ModelResultAPIView.as_view(), name = 'predictions'),
]