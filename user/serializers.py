from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, smart_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.core.mail import EmailMessage
from django.core.validators import MaxLengthValidator
from django.utils import timezone

from .utility import *

from rest_framework.exceptions import AuthenticationFailed
from rest_framework import serializers

import datetime

from chichito import settings
from .models import *
from .services import UserService









class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, max_length=64, write_only=True)
    
    class Meta:
        model = TempUser
        fields = ['email', 'password','phone_number', 'date_joined']
        
    def validate(self, attrs):
        temp_user_ttl = timezone.now() - datetime.timedelta(minutes=1)
        
        email = attrs.get('email')
        password = attrs.get('password')
        

        
        user_email = User.objects.filter(email=email).first()
        
        temp_user_email = TempUser.objects.filter(email=email).first()
        
        if user_email:
            raise serializers.ValidationError('email already exists')
   
        if temp_user_email and temp_user_email.date_joined > temp_user_ttl:
            raise serializers.ValidationError('email already exists')
        
        if temp_user_email and temp_user_email.date_joined < temp_user_ttl:
            temp_user_email.delete()
        
        return attrs

    def create(self, validated_data):
        temp_user = TempUser.objects.create(**validated_data)
        return temp_user
    

class VerifyEmailSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)
    
    def validate(self, attrs):
        otp = attrs.get('otp')
        
        try:
            otp_obj = OneTimePassword.objects.get(otp=otp)
            temp_user = otp_obj.temp_user
            user = User.objects.create_user(email=temp_user.email, password=temp_user.password,username=temp_user.email,phone_number=temp_user.phone_number)
            temp_user.delete()
            return user
            
        except OneTimePassword.DoesNotExist:
            raise serializers.ValidationError('invalid one time password')
    

class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255, write_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'access_token', 'refresh_token']
        
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        request = self.context.get('request')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            temp_user = TempUser.objects.filter(email=email).exists()
            if temp_user:
                raise AuthenticationFailed('please verify your email')
            else:
                raise AuthenticationFailed('wrong password')
        
        if not user.check_password(password):
            raise AuthenticationFailed('Invalid password, try again')
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        tokens = user.tokens()
        
        return {
            'email': user.email,
            'access_token': str(tokens['access']),
            'refresh_token': str(tokens['refresh']),
        }
        
class UserLogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
        
class PasswordResetOTPRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get('email')
        try:
            user = User.objects.get(email=email)
            send_otp_to_user_email(user)
        except User.DoesNotExist:
            raise serializers.ValidationError('User with this email does not exist.')
        return attrs

        
class PasswordResetOTPConfirmSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=8, max_length=64, write_only=True)

    def validate(self, attrs):
        otp = attrs.get('otp')
        new_password = attrs.get('new_password')

        try:
        
            otp_obj = UserOneTimePassword.objects.get(otp=otp)

            if not otp_obj.is_valid():
                raise serializers.ValidationError('OTP has expired.')

            user = otp_obj.user

        
            user.set_password(new_password)
            user.save()

            otp_obj.delete()

        except UserOneTimePassword.DoesNotExist:
            raise serializers.ValidationError('Invalid OTP.')

        return attrs


    

class UserRetriveSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email',  'date_joined',  'profile_image']
        

class UserDeleteSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, max_length=64, write_only=True)
    class Meta:
        model = User
        fields = ['password']
        

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'phone_number', 'email', 
                  'profile_image', 'birth_date', 'address', 'sex', 'date_joined', 'last_login','is_superuser','is_staff']
        read_only_fields = ['id','date_joined', 'last_login','is_superuser','is_staff']
        
        def update(self, instance, validated_data):
            profile_image = validated_data.get('profile_image', instance.profile_image)
            instance.save()
            return instance

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['user', 'balance']
        read_only_fields = ['user']  

    def update(self, instance, validated_data):
        """Handle wallet balance updates"""
        balance = validated_data.get('balance', None)
        if balance:
            instance.balance += balance
        instance.save()
        return instance

class UserToAdminSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

    def validate(self, attrs):
        user_id = attrs.get("user_id")
        try:
            User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")
        return attrs

    def save(self):
        user_id = self.validated_data.get("user_id")
        return UserService.promote_user_to_admin(user_id)
class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username','first_name', 'last_name','date_joined', 'last_login','is_superuser','is_staff']

