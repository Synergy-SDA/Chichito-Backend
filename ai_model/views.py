from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializer import UserSerializer, ResultSerializer
from django.core.cache import cache

class UserInformationAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_202_ACCEPTED)
        return Response(serializer.data ,status = status.HTTP_404_NOT_FOUND)
    
class ModelResultAPIView(APIView):
    def get(self, *args, **kwargs):
        try:
            prediction = cache.get('predictions')
            serializer = ResultSerializer(data = prediction)
            if serializer.is_valid():
                return Response(serializer.data, status = status.HTTP_200_OK)
            
            return Response(serializer.data, status = status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'detail': 'Predictions not found'}, status = status.HTTP_404_NOT_FOUND)
        
        

