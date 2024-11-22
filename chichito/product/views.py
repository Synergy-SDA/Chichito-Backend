from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Product
from .serializers import *
from rest_framework.pagination import PageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# class ProductListView(APIView):
#     @swagger_auto_schema(
#         operation_summary="Retrieve a list of products",
#         responses={
#             200: openapi.Response(
#                 description="List of products retrieved successfully",
#                 schema=openapi.Schema(
#                     type=openapi.TYPE_OBJECT,
#                     properties={
#                         "count": openapi.Schema(type=openapi.TYPE_INTEGER),
#                         "next": openapi.Schema(type=openapi.TYPE_STRING, description="URL to next page"),
#                         "previous": openapi.Schema(type=openapi.TYPE_STRING, description="URL to previous page"),
#                         "results": openapi.Schema(
#                             type=openapi.TYPE_ARRAY,
#                             items=openapi.Items(type=openapi.TYPE_OBJECT, schema=ProductSerializer),
#                         ),
#                     },
#                 ),
#             ),
#         },
#     )
#     def get(self, request, *args, **kwargs):
#         queryset = Product.objects.all()
#         paginator = CustomPagination()
#         paginated_queryset = paginator.paginate_queryset(queryset, request)
#         serializer = ProductSerializer(paginated_queryset, many=True)
#         return paginator.get_paginated_response(serializer.data)

# class ProductAPIView(APIView):
#     @swagger_auto_schema(
#         operation_summary="Create a new product",
#         request_body=ProductSerializer,
#         responses={
#             201: openapi.Response(description="Product created successfully", schema=ProductSerializer),
#             400: "Validation error",
#         },
#     )
#     def post(self, request, *args, **kwargs):
#         serializer = ProductSerializer(data=request.data)
#         if serializer.is_valid():
#             product = serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     @swagger_auto_schema(
#         operation_summary="Retrieve a product by ID",
#         responses={
#             200: openapi.Response(description="Product retrieved successfully", schema=ProductSerializer),
#             404: "Product not found",
#         },
#         manual_parameters=[
#             openapi.Parameter(
#                 "pk",
#                 openapi.IN_PATH,
#                 description="Primary key of the product to retrieve",
#                 type=openapi.TYPE_INTEGER,
#                 required=True,
#             ),
#         ],
#     )
#     def get(self, request, pk=None, *args, **kwargs):
#         product = get_object_or_404(Product, pk=pk)
#         serializer = ProductSerializer(product)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     @swagger_auto_schema(
#         operation_summary="Update a product",
#         request_body=ProductSerializer,
#         responses={
#             200: openapi.Response(description="Product updated successfully", schema=ProductSerializer),
#             400: "Validation error",
#             404: "Product not found",
#         },
#         manual_parameters=[
#             openapi.Parameter(
#                 "pk",
#                 openapi.IN_PATH,
#                 description="Primary key of the product to update",
#                 type=openapi.TYPE_INTEGER,
#                 required=True,
#             ),
#         ],
#     )
#     def put(self, request, pk, *args, **kwargs):
#         product = get_object_or_404(Product, pk=pk)
#         serializer = ProductSerializer(product, data=request.data, partial=False)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     @swagger_auto_schema(
#         operation_summary="Partially update a product",
#         request_body=ProductSerializer,
#         responses={
#             200: openapi.Response(description="Product partially updated successfully", schema=ProductSerializer),
#             400: "Validation error",
#             404: "Product not found",
#         },
#         manual_parameters=[
#             openapi.Parameter(
#                 "pk",
#                 openapi.IN_PATH,
#                 description="Primary key of the product to partially update",
#                 type=openapi.TYPE_INTEGER,
#                 required=True,
#             ),
#         ],
#     )
#     def patch(self, request, pk, *args, **kwargs):
#         product = get_object_or_404(Product, pk=pk)
#         serializer = ProductSerializer(product, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     @swagger_auto_schema(
#         operation_summary="Delete a product",
#         responses={
#             204: "Product deleted successfully",
#             404: "Product not found",
#         },
#         manual_parameters=[
#             openapi.Parameter(
#                 "pk",
#                 openapi.IN_PATH,
#                 description="Primary key of the product to delete",
#                 type=openapi.TYPE_INTEGER,
#                 required=True,
#             ),
#         ],
#     )
#     def delete(self, request, pk, *args, **kwargs):
#         product = get_object_or_404(Product, pk=pk)
#         product.delete()
#         return Response({"message": "Product deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

# class FeatureAPIView(APIView):
#     @swagger_auto_schema(
#         operation_summary="Create a new feature",
#         request_body=FeatureSerializer,
#         responses={
#             201: openapi.Response(description="Feature created successfully", schema=FeatureSerializer),
#             400: "Validation error",
#         },
#     )
#     def post(self, request, *args, **kwargs):
#         serializer = FeatureSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     @swagger_auto_schema(
#         operation_summary="Retrieve feature(s)",
#         responses={
#             200: openapi.Response(description="Feature(s) retrieved successfully", schema=FeatureSerializer(many=True)),
#             404: "Feature not found",
#         },
#         manual_parameters=[
#             openapi.Parameter(
#                 "pk",
#                 openapi.IN_PATH,
#                 description="Primary key of the feature to retrieve (optional). If not provided, retrieves all features.",
#                 type=openapi.TYPE_INTEGER,
#                 required=True,
#             ),
#         ],
#     )
#     def get(self, request, pk=None, *args, **kwargs):
#         if pk:
#             try:
#                 feature = Feature.objects.get(pk=pk)
#             except Feature.DoesNotExist:
#                 return Response({"detail": "Feature not found."}, status=status.HTTP_404_NOT_FOUND)
#             serializer = FeatureSerializer(feature)
#             return Response(serializer.data)
#         else:
#             features = Feature.objects.all()
#             serializer = FeatureSerializer(features, many=True)
#             return Response(serializer.data)

#     @swagger_auto_schema(
#         operation_summary="Update a feature",
#         request_body=FeatureSerializer,
#         responses={
#             200: openapi.Response(description="Feature updated successfully", schema=FeatureSerializer),
#             400: "Validation error",
#             404: "Feature not found",
#         },
#         manual_parameters=[
#             openapi.Parameter(
#                 "pk",
#                 openapi.IN_PATH,
#                 description="Primary key of the feature to update",
#                 type=openapi.TYPE_INTEGER,
#                 required=True,
#             ),
#         ],
#     )
#     def put(self, request, pk, *args, **kwargs):
#         try:
#             feature = Feature.objects.get(pk=pk)
#         except Feature.DoesNotExist:
#             return Response({"detail": "Feature not found."}, status=status.HTTP_404_NOT_FOUND)

#         serializer = FeatureSerializer(feature, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     @swagger_auto_schema(
#         operation_summary="Delete a feature",
#         responses={
#             204: "Feature deleted successfully",
#             404: "Feature not found",
#         },
#         manual_parameters=[
#             openapi.Parameter(
#                 "pk",
#                 openapi.IN_PATH,
#                 description="Primary key of the feature to delete",
#                 type=openapi.TYPE_INTEGER,
#                 required=True,
#             ),
#         ],
#     )
#     def delete(self, request, pk, *args, **kwargs):
#         try:
#             feature = Feature.objects.get(pk=pk)
#         except Feature.DoesNotExist:
#             return Response({"detail": "Feature not found."}, status=status.HTTP_404_NOT_FOUND)

#         feature.delete()
#         return Response({"detail": "Feature deleted."}, status=status.HTTP_204_NO_CONTENT)
# class FeatureValueAPIView(APIView):
#     @swagger_auto_schema(
#         operation_summary="Create a new feature value",
#         request_body=FeatureValueSerializer,
#         responses={
#             201: openapi.Response(description="Feature value created successfully", schema=FeatureValueSerializer),
#             400: "Validation error",
#         },
#     )
#     def post(self, request, *args, **kwargs):
#         serializer = FeatureValueSerializer(data=request.data)
#         if serializer.is_valid():
#             feature_value = serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     @swagger_auto_schema(
#         operation_summary="Retrieve feature value(s)",
#         responses={
#             200: openapi.Response(description="Feature value(s) retrieved successfully", schema=FeatureValueSerializer(many=True)),
#             404: "Feature value not found",
#         },
#         manual_parameters=[
#             openapi.Parameter(
#                 "pk",
#                 openapi.IN_PATH,
#                 description="Primary key of the feature value to retrieve (optional). If not provided, retrieves all feature values.",
#                 type=openapi.TYPE_INTEGER,
#                 required=True,
#             ),
#             openapi.Parameter(
#                 "feature",
#                 openapi.IN_QUERY,
#                 description="Filter feature values by feature name (optional)",
#                 type=openapi.TYPE_STRING,
#                 required=False,
#             ),
#         ],
#     )
#     def get(self, request, pk=None, *args, **kwargs):
#         if pk:
#             try:
#                 feature_value = FeatureValue.objects.get(pk=pk)
#             except FeatureValue.DoesNotExist:
#                 return Response({"detail": "Feature value not found."}, status=status.HTTP_404_NOT_FOUND)
#             serializer = FeatureValueSerializer(feature_value)
#             return Response(serializer.data)
#         else:
#             feature_name = request.query_params.get('feature')
#             if feature_name:
#                 feature_values = FeatureValue.objects.filter(feature__name=feature_name)
#             else:
#                 feature_values = FeatureValue.objects.all()
#             serializer = FeatureValueSerializer(feature_values, many=True)
#             return Response(serializer.data)

#     @swagger_auto_schema(
#         operation_summary="Update a feature value",
#         request_body=FeatureValueSerializer,
#         responses={
#             200: openapi.Response(description="Feature value updated successfully", schema=FeatureValueSerializer),
#             400: "Validation error",
#             404: "Feature value not found",
#         },
#         manual_parameters=[
#             openapi.Parameter(
#                 "pk",
#                 openapi.IN_PATH,
#                 description="Primary key of the feature value to update",
#                 type=openapi.TYPE_INTEGER,
#                 required=True,
#             ),
#         ],
#     )
#     def put(self, request, pk, *args, **kwargs):
#         try:
#             feature_value = FeatureValue.objects.get(pk=pk)
#         except FeatureValue.DoesNotExist:
#             return Response({"detail": "Feature value not found."}, status=status.HTTP_404_NOT_FOUND)
#         serializer = FeatureValueSerializer(feature_value, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     @swagger_auto_schema(
#         operation_summary="Delete a feature value",
#         responses={
#             204: "Feature value deleted successfully",
#             404: "Feature value not found",
#         },
#         manual_parameters=[
#             openapi.Parameter(
#                 "pk",
#                 openapi.IN_PATH,
#                 description="Primary key of the feature value to delete",
#                 type=openapi.TYPE_INTEGER,
#                 required=True,
#             ),
#         ],
#     )
#     def delete(self, request, pk, *args, **kwargs):
#         try:
#             feature_value = FeatureValue.objects.get(pk=pk)
#         except FeatureValue.DoesNotExist:
#             return Response({"detail": "Feature value not found."}, status=status.HTTP_404_NOT_FOUND)
#         feature_value.delete()
#         return Response({"detail": "Feature value deleted."}, status=status.HTTP_204_NO_CONTENT)

# class ProductPerCategoryAPIView(APIView):
#     @swagger_auto_schema(
#         operation_summary="Retrieve a list of products by category",
#         operation_description="Fetch products belonging to a specific category.",
#         parameters=[
#             openapi.Parameter(
#                 'category_name', openapi.IN_PATH, description="Name of the category", type=openapi.TYPE_STRING
#             ),
#         ],
#         responses={
#             200: openapi.Response(
#                 description="List of products for the specified category retrieved successfully",
#                 schema=openapi.Schema(
#                     type=openapi.TYPE_ARRAY,
#                     items=openapi.Items(type=openapi.TYPE_OBJECT, schema=ProductSerializer),
#                 ),
#             ),
#             404: openapi.Response(
#                 description="Category not found",
#                 schema=openapi.Schema(type=openapi.TYPE_OBJECT, properties={"detail": openapi.Schema(type=openapi.TYPE_STRING)}),
#             ),
#         },
#     )
#     def get(self, request, category_name, *args, **kwargs):
#         category = get_object_or_404(Category, name=category_name)
#         products = Product.objects.filter(category=category)
#         serializer = ProductSerializer(products, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)


from rest_framework import viewsets
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .models import Product
from .serializers import ProductSerializer

class ProductListView(viewsets.ModelViewSet):
    queryset = Product.objects.all()  
    serializer_class = ProductSerializer  

    @swagger_auto_schema(
        operation_summary="Retrieve a list of products",
        responses={
            200: openapi.Response(
                description="List of products retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "count": openapi.Schema(type=openapi.TYPE_INTEGER, description="Total number of products"),
                        "next": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, description="Next page URL"),
                        "previous": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, description="Previous page URL"),
                        "results": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_INTEGER, description="Product ID"),
                                    "name": openapi.Schema(type=openapi.TYPE_STRING, description="Product name"),
                                    "price": openapi.Schema(type=openapi.TYPE_NUMBER, description="Product price"),
                                },
                            ),
                        ),
                    },
                ),
            ),
        },
    )
    def list(self, request, *args, **kwargs):
 
        queryset = self.get_queryset()  
        paginator = CustomPagination()  #
        paginated_queryset = paginator.paginate_queryset(queryset, request)  
        serializer = self.get_serializer(paginated_queryset, many=True)  
        return paginator.get_paginated_response(serializer.data)
