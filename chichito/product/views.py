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
from rest_framework import status
from django.db import connection


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ProductListView(ViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @swagger_auto_schema(
        operation_summary="List all products with pagination",
        responses={
            200: openapi.Response(
                "A list of products with pagination",
                ProductSerializer(many=True)
            ),
        },
    )
    def list(self, request, *args, **kwargs):
        queryset = Product.objects.all()
        paginator = CustomPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = ProductSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)


class ProductViewSet(ViewSet):
    
    @swagger_auto_schema(
        operation_summary="Create a new product",
        request_body=ProductSerializer,
        responses={
            201: openapi.Response(description="Product created successfully", schema=ProductSerializer),
            400: "Validation error",
        },
    )
    def create(self, request, *args, **kwargs):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Retrieve a product by ID",
        responses={
            200: openapi.Response(description="Product retrieved successfully", schema=ProductSerializer),
            404: "Product not found",
        },
    )
    def retrieve(self, request, pk=None, *args, **kwargs):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Update a product",
        request_body=ProductSerializer,
        responses={
            200: openapi.Response(description="Product updated successfully", schema=ProductSerializer),
            400: "Validation error",
            404: "Product not found",
        },
    )
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

    @swagger_auto_schema(
        operation_summary="Partially update a product",
        request_body=ProductSerializer,
        responses={
            200: openapi.Response(description="Product partially updated successfully", schema=ProductSerializer),
            400: "Validation error",
            404: "Product not found",
        },
    )
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

    @swagger_auto_schema(
        operation_summary="Delete a product",
        responses={
            204: "Product deleted successfully",
            404: "Product not found",
        },
    )
    def destroy(self, request, pk=None, *args, **kwargs):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        product.delete()
        return Response({"detail": "Product deleted."}, status=status.HTTP_204_NO_CONTENT)


class FeatureViewSet(ViewSet):
    
    @swagger_auto_schema(
        operation_summary="Create a new feature",
        request_body=FeatureSerializer,
        responses={
            201: openapi.Response(description="Feature created successfully", schema=FeatureSerializer),
            400: "Validation error",
        },
    )
    def create(self, request, *args, **kwargs):
        serializer = FeatureSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Retrieve feature(s)",
        responses={
            200: openapi.Response(description="Feature(s) retrieved successfully", schema=FeatureSerializer(many=True)),
            404: "Feature not found",
        },
    )
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

    @swagger_auto_schema(
        operation_summary="Update a feature",
        request_body=FeatureSerializer,
        responses={
            200: openapi.Response(description="Feature updated successfully", schema=FeatureSerializer),
            400: "Validation error",
            404: "Feature not found",
        },
    )
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

    @swagger_auto_schema(
        operation_summary="Delete a feature",
        responses={
            204: "Feature deleted successfully",
            404: "Feature not found",
        },
    )
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

    @swagger_auto_schema(
        operation_summary="Create a new feature value",
        request_body=FeatureValueSerializer,
        responses={
            201: openapi.Response(description="Feature value created successfully", schema=FeatureValueSerializer),
            400: "Validation error",
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve feature value(s)",
        responses={
            200: openapi.Response(description="Feature value(s) retrieved successfully", schema=FeatureValueSerializer(many=True)),
            404: "Feature value not found",
        },
    )
    def list(self, request, *args, **kwargs):
        feature_name = request.query_params.get('feature')
        if feature_name:
            feature_values = FeatureValue.objects.filter(feature__name=feature_name)
        else:
            feature_values = FeatureValue.objects.all()
        serializer = FeatureValueSerializer(feature_values, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Update a feature value",
        request_body=FeatureValueSerializer,
        responses={
            200: openapi.Response(description="Feature value updated successfully", schema=FeatureValueSerializer),
            400: "Validation error",
            404: "Feature value not found",
        },
    )
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

    @swagger_auto_schema(
        operation_summary="Delete a feature value",
        responses={
            204: "Feature value deleted successfully",
            404: "Feature value not found",
        },
    )
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

    @swagger_auto_schema(
        operation_summary="Retrieve a list of products by category",
        operation_description="Fetch products belonging to a specific category.",
        parameters=[
            openapi.Parameter(
                'category_name', openapi.IN_PATH, description="Name of the category", type=openapi.TYPE_STRING
            ),
        ],
        responses={
            200: openapi.Response(
                description="List of products for the specified category retrieved successfully",
                schema=ProductSerializer(many=True),
            ),
            404: openapi.Response(
                description="Category not found",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={"detail": openapi.Schema(type=openapi.TYPE_STRING)}),
            ),
        },
    )
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

    @swagger_auto_schema(
        operation_summary="Filter products by category and features",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'category': openapi.Schema(type=openapi.TYPE_INTEGER, description="Category ID"),
                'features': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'name': openapi.Schema(type=openapi.TYPE_STRING, description="Feature name"),
                            'value': openapi.Schema(type=openapi.TYPE_STRING, description="Feature value"),
                        },
                    ),
                    description="List of features to filter by (e.g., [{'name': 'color', 'value': 'red'}])"
                ),
            },
            required=[],
        ),
        responses={200: ProductSerializer(many=True)},
    )
    @action(detail=False, methods=['post'])
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
    pass 
