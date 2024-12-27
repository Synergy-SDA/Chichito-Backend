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
        cache_key = 'predictions'
        prediction = cache.get(cache_key)
        
        if prediction is None:
            return Response({'detail': 'Predictions not found in cache'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ResultSerializer(data=prediction, many=True)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response({'detail': 'Invalid prediction data'}, status=status.HTTP_400_BAD_REQUEST)
        
        

