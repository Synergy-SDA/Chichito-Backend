from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated

from .utility import send_otp_email
from .serializers import *
from .models import *


class RegisterUserView(APIView):
    serializer_class = UserCreateSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            temp_user = serializer.data
            send_otp_email(temp_user['email'])
            return Response({
                'data': temp_user,
                'message': 'User created successfully\n Please check your email for One Time Password',
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class VerifyEmailView(APIView):
    serializer_class = VerifyEmailSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            return Response({
                'message': 'account verified successfully',
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LoginUserView(APIView):
    serializer_class = UserLoginSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})

        if serializer.is_valid(raise_exception=True):
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    serializer_class = PasswordResetOTPRequestSerializer
    def post(self, request):
        serializer = PasswordResetOTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"message": "OTP sent to email."}, status=status.HTTP_200_OK)

 
class PasswordResetConfirmView(APIView):
    serializer_class = PasswordResetOTPConfirmSerializer
    def post(self, request):
        serializer = PasswordResetOTPConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)

class LogoutUserView(APIView):
    serializer_class = UserLogoutSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        refresh_token = serializer.validated_data.get('refresh_token')
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response("logout successfully", status=status.HTTP_200_OK)
        except:
            return Response("invalid token", status=status.HTTP_400_BAD_REQUEST)
        
class UserRetriveView(APIView):
    serializer_class= UserRetriveSerializer
    
    def get(self, request, *args, **kwargs):
        if (not request.user.is_authenticated):
            return Response("user not authenticated", status=status.HTTP_401_UNAUTHORIZED)
        username = request.user.username
        user = User.objects.get(username=username)
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class UserDeleteView(APIView):
    serializer_class= UserDeleteSerializer
    
    def delete(self, request, *args, **kwargs):
        if (not request.user.is_authenticated):
            return Response("user not authenticated", status=status.HTTP_401_UNAUTHORIZED)
        
        email = request.user.email
        user = User.objects.get(email=email)
        serializer = self.serializer_class(data = request.data)
        
        serializer.is_valid(raise_exception=True)
        
        if user.check_password(serializer.validated_data.get('password')):
            return Response("invalid password", status=status.HTTP_400_BAD_REQUEST)
        
        user.delete()
        return Response("user deleted successfully", status=status.HTTP_200_OK)

        

class UserUpdateView(APIView):
    serializer_class= UserUpdateSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def patch(self, request, *args, **kwargs):
        try:
            email = request.user.email
            user = User.objects.get(email=email)
            serializer = self.serializer_class(user, data = request.data, partial=True)
        
            if serializer.is_valid():
                serializer.update(user, serializer.validated_data)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except User.DoesNotExist:
            return Response("user not found", status=status.HTTP_404_NOT_FOUND)
        
class WalletDetailView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WalletSerializer

    def get(self, request):
        try:
            wallet = Wallet.objects.get(user=request.user)
            serializer = self.serializer_class(wallet)  # Serialize the object
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Wallet.DoesNotExist:
            return Response({"detail": "Wallet not found."}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request):
        try:
            wallet = Wallet.objects.get(user=request.user)
            serializer = self.serializer_class(wallet, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Wallet.DoesNotExist:
            return Response({"detail": "Wallet not found."}, status=status.HTTP_404_NOT_FOUND)
