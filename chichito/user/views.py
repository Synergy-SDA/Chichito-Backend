from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth import authenticate
from .serializers import UserSignupSerializer, UserLoginSerializer
from .utils import OTPService
from .models import User,OTP

# class UserSignupView(APIView):
#     @swagger_auto_schema(
#         operation_summary="User Signup",
#         operation_description="Create a new user and return JWT tokens.",
#         request_body=UserSignupSerializer,  
#         responses={
#             201: openapi.Response(
#                 description="Signup successful.",
#                 examples={
#                     "application/json": {
#                         "refresh": "refresh_token_example",
#                         "access": "access_token_example",
#                         "user": {
#                             "username": "mehrshad",
#                             "first_name": "Hosein",
#                             "last_name": "Ali",
#                             "phone_number": "09123456788",
#                             "mail": "mehsahd@gmail.com",
#                             "birth_date": "1995-05-15",
#                             "address": "Street 123",
#                             "sex": "M"
#                         }
#                     }
#                 },
#             ),
#             400: openapi.Response(
#                 description="Invalid data.",
#                 examples={
#                     "application/json": {"username": ["This field is required."]}
#                 },
#             ),
#         },
#     )
#     def post(self, request):
#         serializer = UserSignupSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save()
#             refresh = RefreshToken.for_user(user)
#             return Response({
#                 "refresh": str(refresh),
#                 "access": str(refresh.access_token),
#                 "user": serializer.data
#             }, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
                        "message": "Signup successful. Please check your email for OTP.",
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
            # Save the user to the database
            user = serializer.save()

            # Generate and send OTP for email verification
            try:
                OTPService.generate_otp(user)
            except Exception as e:
                # If OTP generation fails, delete the user to maintain consistency
                user.delete()
                return Response(
                    {"error": "Failed to send OTP. Please try again later."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                "message": "Signup successful. Please check your email for OTP.",
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
class VerifyOTPView(APIView):
    @swagger_auto_schema(
        operation_summary="Verify OTP",
        operation_description="Verify the OTP sent to the user's email.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'mail': openapi.Schema(type=openapi.TYPE_STRING, description='User email'),
                'otp': openapi.Schema(type=openapi.TYPE_STRING, description='OTP code')
            },
            required=['mail', 'otp']
        ),
        responses={
            200: openapi.Response(description="OTP verified successfully."),
            400: openapi.Response(description="Invalid OTP or OTP expired.")
        },
    )
    def post(self, request):
        mail = request.data.get('mail')
        otp = request.data.get('otp')

        if not mail or not otp:
            return Response({"error": "Email and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(mail=mail)
            otp_record = OTP.objects.get(user=user)

            if otp_record.is_expired():
                return Response({"error": "OTP has expired. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)

            if otp_record.otp != otp:
                return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

            
            user.is_verified = True
            user.save()

            
            otp_record.delete()

            return Response({"message": "OTP verified successfully."}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except OTP.DoesNotExist:
            return Response({"error": "OTP not found."}, status=status.HTTP_404_NOT_FOUND)
