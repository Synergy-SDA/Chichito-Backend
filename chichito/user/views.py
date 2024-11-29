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
from django.contrib.auth.hashers import make_password
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
        
            user = serializer.save()

            
            try:
                OTPService.generate_otp(user,purpose="email_verification")
            except Exception as e:
            
                user.delete()
                return Response(
                    {"error": "Failed to send OTP. Please try again later."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            
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
class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(mail=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        
        OTPService.generate_otp(user, purpose="password_reset")

        return Response({"message": "OTP sent successfully to your email."}, status=status.HTTP_200_OK)



class VarifyForgotPasswordOTPView(APIView):
    @swagger_auto_schema(
        operation_summary="Reset Password",
        operation_description="Verify the OTP and reset the user's password.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
                'otp': openapi.Schema(type=openapi.TYPE_STRING, maxLength=6),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_PASSWORD)
            },
            required=['email', 'otp', 'new_password']
        ),
        responses={
            200: openapi.Response(
                description="Password reset successful.",
                examples={"application/json": {"message": "Password reset successful."}}
            ),
            400: openapi.Response(
                description="Invalid OTP or data.",
                examples={"application/json": {"error": "Invalid OTP or OTP has expired."}}
            )
        }
    )
    def post(self, request):
        # Extract data from the request
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')

        # Check if the user exists
        try:
            user = User.objects.get(mail=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        # Verify OTP
        otp_record = getattr(user, 'otp_record', None)  # Safely get the related OTP record
        if not otp_record or otp_record.otp != otp or otp_record.is_expired():
            return Response({"error": "Invalid OTP or OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)

        # Reset the password
        user.password = make_password(new_password)
        user.save()

        # Delete OTP record after successful password reset
        otp_record.delete()

        return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)

class VerifyEmailOTPView(APIView):
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
