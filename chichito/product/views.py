from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Product
from .serializers import *
from rest_framework.pagination import PageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from django.db.models.functions import Lower
from drf_yasg import openapi 
from rest_framework import status
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.filters import SearchFilter 
from rest_framework.views import APIView


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ProductListView(ViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

 
    def list(self, request, *args, **kwargs):
        queryset = Product.objects.all()
        paginator = CustomPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = ProductSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)


class ProductViewSet(ViewSet):
    
   
    def create(self, request, *args, **kwargs):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  
    def retrieve(self, request, pk=None, *args, **kwargs):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product)
        return Response(serializer.data)

  
    def update(self, request, pk=None, *args, **kwargs):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None, *args, **kwargs):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  
    def destroy(self, request, pk=None, *args, **kwargs):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        product.delete()
        return Response({"detail": "Product deleted."}, status=status.HTTP_204_NO_CONTENT)


class FeatureViewSet(ViewSet):
    
 
    def create(self, request, *args, **kwargs):
        serializer = FeatureSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

   
    def retrieve(self, request, pk=None, *args, **kwargs):
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

 
    def update(self, request, pk=None, *args, **kwargs):
        try:
            feature = Feature.objects.get(pk=pk)
        except Feature.DoesNotExist:
            return Response({"detail": "Feature not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = FeatureSerializer(feature, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, pk=None, *args, **kwargs):
        try:
            feature = Feature.objects.get(pk=pk)
        except Feature.DoesNotExist:
            return Response({"detail": "Feature not found."}, status=status.HTTP_404_NOT_FOUND)

        feature.delete()
        return Response({"detail": "Feature deleted."}, status=status.HTTP_204_NO_CONTENT)


class FeatureValueViewSet(ViewSet):
    """
    A ViewSet for managing feature values.
    """
    queryset = FeatureValue.objects.all()
    serializer_class = FeatureValueSerializer

  
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

  
    def list(self, request, *args, **kwargs):
        feature_name = request.query_params.get('feature')
        if feature_name:
            feature_values = FeatureValue.objects.filter(feature__name=feature_name)
        else:
            feature_values = FeatureValue.objects.all()
        serializer = FeatureValueSerializer(feature_values, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

   
    def update(self, request, pk=None, *args, **kwargs):
        try:
            feature_value = FeatureValue.objects.get(pk=pk)
        except FeatureValue.DoesNotExist:
            return Response({"detail": "Feature value not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = FeatureValueSerializer(feature_value, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  
    def destroy(self, request, pk=None, *args, **kwargs):
        try:
            feature_value = FeatureValue.objects.get(pk=pk)
        except FeatureValue.DoesNotExist:
            return Response({"detail": "Feature value not found."}, status=status.HTTP_404_NOT_FOUND)

        feature_value.delete()
        return Response({"detail": "Feature value deleted."}, status=status.HTTP_204_NO_CONTENT)


class ProductPerCategoryViewSet(ViewSet):
    """
    A ViewSet for listing products by category.
    """

    def list(self, request, category_name=None, *args, **kwargs):
        try:
            # Retrieve the category by its name
            category = Category.objects.get(name=category_name)
        except Category.DoesNotExist:
            return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

        # Filter products by category
        products = Product.objects.filter(category=category)
        serializer = ProductSerializer(products, many=True)

        # Return the serialized products data
        return Response(serializer.data, status=status.HTTP_200_OK)





class ProductFilter(ViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def filter_products(self, request):
        category_id = request.data.get('category', None)
        features = request.data.get('features', [])

        queryset = Product.objects.all()

        if category_id:
            queryset = queryset.filter(category__id=category_id)

        if features:
            for feature in features:
                feature_name = feature.get('name')
                feature_value = feature.get('value')
                if feature_name and feature_value:
                    feature_value_obj = FeatureValue.objects.filter(
                        feature__name=feature_name, value=feature_value
                    ).first()
                    if feature_value_obj:
                        queryset = queryset.filter(features=feature_value_obj)

        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProductSearchViewSet(ViewSet):

    def search(self, request):
        query = request.query_params.get("query", None)

        if not query:
            return Response({"error": "Query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

       
        products = Product.objects.filter(name__icontains=query)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)



class ProductSortMinViewSet(ViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    def sort_by_min_price(self, request):
        sorted_products = Product.objects.all().order_by('price') 
        serializer = ProductSerializer(sorted_products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ProductSortMaxViewSet(ViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    def sort_by_min_price(self, request):
        sorted_products = Product.objects.all().order_by('-price') 
        serializer = ProductSerializer(sorted_products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




class ProductSortByNameViewSet(ViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

  
    def sort_by_name(self, request):
        """
        API to sort products by name.
        Use ?order=asc/desc for ascending or descending order.
        """
        order = request.query_params.get('order', 'asc').lower()

        # Validate `order` parameter
        is_desc = order == 'desc'

        # Case-insensitive sorting by name
        sorted_products = Product.objects.all().order_by(
            Lower('name').desc() if is_desc else Lower('name')
        )

        serializer = ProductSerializer(sorted_products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductSearchViewSet(ViewSet):
 
    def search(self, request):
        query = request.query_params.get("query", None)

        if not query:
            return Response({"error": "Query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

       
        products = Product.objects.filter(name__icontains=query)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    


class CommentCreate(APIView):
    serializer_class = CommentCreateSerializer
      
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({
                'message': 'comment created succesfuly', 
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)