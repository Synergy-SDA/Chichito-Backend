from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed


class UserSignupSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, required=True, min_length=8)
    password2 = serializers.CharField(write_only=True, required=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'phone_number', 'mail', 'birth_date', 'address', 'sex', 'password1', 'password2']
        extra_kwargs = {
            'username': {'required': True, 'min_length': 5},
            'mail': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        
        return data

    def create(self, validated_data):
        password = validated_data.pop('password1')
        validated_data.pop('password2')
        
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        return user



class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])

        if not user:
            raise AuthenticationFailed('Invalid username or password')

        data['user'] = user
        return data

