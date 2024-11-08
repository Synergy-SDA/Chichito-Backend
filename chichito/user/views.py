from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSignupSerializer
from .models import User
from rest_framework.response import Response

from .serializers import UserSerializer
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

from django.shortcuts import get_object_or_404

from rest_framework.decorators import authentication_classes , permission_classes
from rest_framework.authentication import SessionAuthentication , TokenAuthentication
from rest_framework.permissions import IsAuthenticated



class UserSignupView(APIView):
    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            token = Token.objects.create(user=user)
            return Response({"token" : token.key ,
                        "user": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    def post(self , request):
        user = get_object_or_404(User , username = request.data['username'])
        


def login(request):
    user = get_object_or_404(User , username = request.data['username'])
    if not user.check_password(request.data['password']):
        return Response({"detail" : "not found"} , status=status.HTTP_404_NOT_FOUND)
    token , created = Token.objects.get_or_create(user = user)
    serializer = UserSerializer(instance = user)
    return Response({"token" : token.key ,
                        "user": serializer.data})



def post(self, request):
    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data.get('user')
        
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)