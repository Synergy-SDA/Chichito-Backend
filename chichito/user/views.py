from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth import authenticate
from .serializers import UserSignupSerializer, UserLoginSerializer


class UserSignupView(APIView):
    @swagger_auto_schema(
        operation_summary="User Signup",
        operation_description="Create a new user and return JWT tokens.",
        request_body=UserSignupSerializer,  
        responses={
            201: openapi.Response(
                description="Signup successful.",
                examples={
                    "application/json": {
                        "refresh": "refresh_token_example",
                        "access": "access_token_example",
                        "user": {
                            "username": "mehrshad",
                            "first_name": "Hosein",
                            "last_name": "Ali",
                            "phone_number": "09123456788",
                            "mail": "mehsahd@gmail.com",
                            "birth_date": "1995-05-15",
                            "address": "Street 123",
                            "sex": "M"
                        }
                    }
                },
            ),
            400: openapi.Response(
                description="Invalid data.",
                examples={
                    "application/json": {"username": ["This field is required."]}
                },
            ),
        },
    )
    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    @swagger_auto_schema(
        operation_summary="User Login",
        operation_description="Authenticate user and return JWT tokens.",
        request_body=UserLoginSerializer, 
        responses={
            200: openapi.Response(
                description="Login successful.",
                examples={
                    "application/json": {
                        "refresh": "refresh_token_example",
                        "access": "access_token_example"
                    }
                },
            ),
            401: openapi.Response(
                description="Invalid credentials.",
                examples={
                    "application/json": {"detail": "Invalid username or password"}
                },
            ),
        },
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }, status=status.HTTP_200_OK)
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
