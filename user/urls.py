from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', RegisterUserView.as_view()),
    path('verify-email/', VerifyEmailView.as_view()),
    
    path('login/', LoginUserView.as_view()),
    path('logout/', LogoutUserView.as_view()),

    
    path('password-reset/', PasswordResetRequestView.as_view()),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    path('users/retrieve/', UserRetriveView.as_view()),
    path('users/delete/', UserDetailView.as_view()),
    path('user/detail/', UserDetailView.as_view(), name='user-detail'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('wallet/', WalletDetailView.as_view(), name='wallet-detail'),

    path('make-user-admin/', MakeUserAdminView.as_view(), name='make-user-admin'),

    path('users-list/', ListUsersView.as_view(), name='list-users'),
]