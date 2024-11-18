from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Product
from .serializers import *
from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# class ProductListView(APIView):
#     def get(self, request, *args, **kwargs):
#         queryset = Product.objects.all()
#         paginator = CustomPagination()
#         paginated_queryset = paginator.paginate_queryset(queryset, request)
#         serializer = ProductSerializer(paginated_queryset, many=True)
#         return paginator.get_paginated_response(serializer.data)



# class ProductAPIView(APIView):
#     def post(self, request, *args, **kwargs):
#         serializer = ProductSerializer(data=request.data)
#         if serializer.is_valid():
#             product = serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#     def get(self, request, pk=None, *args, **kwargs):
#         product = get_object_or_404(Product, pk=pk)
#         serializer = ProductSerializer(product)
#         return Response(serializer.data, status=status.HTTP_200_OK)


#     def put(self, request, pk, *args, **kwargs):
#         product = get_object_or_404(Product, pk=pk)
#         serializer = ProductSerializer(product, data=request.data, partial=False)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def patch(self, request, pk, *args, **kwargs):
#         product = get_object_or_404(Product, pk=pk)
#         serializer = ProductSerializer(product, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk, *args, **kwargs):
#         product = get_object_or_404(Product, pk=pk)
#         product.delete()
#         return Response({"message": "Product deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class FeatureAPIView(APIView):
    
    def post(self, request, *args, **kwargs):
        serializer = FeatureSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    def get(self, request, pk=None, *args, **kwargs):
        if pk:
            try:
                feature = Feature.objects.get(pk=pk)
            except Feature.DoesNotExist:
                return Response({"detail": "Feature not found."}, status=status.HTTP_404_NOT_FOUND)
            serializer = FeatureSerializer(feature)
            return Response(serializer.data)
        else:
            features = Feature.objects.all()
            serializer = FeatureSerializer(features, many=True)
            return Response(serializer.data)

    
    def put(self, request, pk, *args, **kwargs):
        try:
            feature = Feature.objects.get(pk=pk)
        except Feature.DoesNotExist:
            return Response({"detail": "Feature not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = FeatureSerializer(feature, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    def delete(self, request, pk, *args, **kwargs):
        try:
            feature = Feature.objects.get(pk=pk)
        except Feature.DoesNotExist:
            return Response({"detail": "Feature not found."}, status=status.HTTP_404_NOT_FOUND)
        
        feature.delete()
        return Response({"detail": "Feature deleted."}, status=status.HTTP_204_NO_CONTENT)


class FeatureValueAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = FeatureValueSerializer(data=request.data)
        if serializer.is_valid():
            feature_value = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None, *args, **kwargs):
        if pk:
            try:
                feature_value = FeatureValue.objects.get(pk=pk)
            except FeatureValue.DoesNotExist:
                return Response({"detail": "Feature value not found."}, status=status.HTTP_404_NOT_FOUND)
            serializer = FeatureValueSerializer(feature_value)
            return Response(serializer.data)
        else:
            feature_name = request.query_params.get('feature')
            if feature_name:
                feature_values = FeatureValue.objects.filter(feature__name=feature_name)
            else:
                feature_values = FeatureValue.objects.all()
            serializer = FeatureValueSerializer(feature_values, many=True)
            return Response(serializer.data)


    def put(self, request, pk, *args, **kwargs):
        try:
            feature_value = FeatureValue.objects.get(pk=pk)
        except FeatureValue.DoesNotExist:
            return Response({"detail": "Feature value not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = FeatureValueSerializer(feature_value, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk, *args, **kwargs):
        try:
            feature_value = FeatureValue.objects.get(pk=pk)
        except FeatureValue.DoesNotExist:
            return Response({"detail": "Feature value not found."}, status=status.HTTP_404_NOT_FOUND)
        
        feature_value.delete()
        return Response({"detail": "Feature value deleted."}, status=status.HTTP_204_NO_CONTENT)
