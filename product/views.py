from rest_framework.response import Response
from rest_framework import status
from .models import Product
from .serializers import *
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from django.db.models.functions import Lower
from rest_framework import status
from drf_spectacular.utils import extend_schema,OpenApiParameter, OpenApiExample
import json
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser



class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ProductListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        queryset = Product.objects.all()
        paginator = CustomPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = ProductSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

class ProductAPIView(APIView):
    @extend_schema(
        request=ProductSerializer,
        responses=ProductSerializer,
        description="Create a new product"
    )
    def post(self, request, *args, **kwargs):
        """Create a new product."""
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None, *args, **kwargs):
        """Retrieve a single product by ID."""
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product)
        return Response(serializer.data)

    @extend_schema(
        request=ProductSerializer,
        responses=ProductSerializer,
        description="Create a new product"
    )
    def put(self, request, pk=None, *args, **kwargs):
        """Update a product completely."""
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=ProductSerializer,
        responses=ProductSerializer,
        description="Create a new product"
    )
    def patch(self, request, pk=None, *args, **kwargs):
        """Partially update a product."""
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None, *args, **kwargs):
        """Delete a product."""
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        product.delete()
        return Response({"detail": "Product deleted."}, status=status.HTTP_204_NO_CONTENT)

class FeatureListAPIView(APIView):

    @extend_schema(
        request=FeatureSerializer,
        responses=FeatureSerializer,
        description="Get all features"
    )
    def get(self, request, *args, **kwargs):
        features = Feature.objects.all()
        serializer = FeatureSerializer(features, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
class FeatureAPIView(APIView):
    @extend_schema(
        request=FeatureSerializer,
        responses=FeatureSerializer,
        description="Create a new Feature"
    )
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
    @extend_schema(
        operation_id="Update Feature",
        description="Update a feature by its ID.",
        request=FeatureSerializer,
        responses={200: FeatureSerializer, 400: {"type": "object", "properties": {"detail": {"type": "string"}}}},
    )
    def put(self, request, pk=None, *args, **kwargs):
        try:
            feature = Feature.objects.get(pk=pk)
        except Feature.DoesNotExist:
            return Response({"detail": "Feature not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = FeatureSerializer(feature, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        operation_id="Delete Feature",
        description="Delete a feature by its ID.",
        responses={204: {"type": "object", "properties": {"detail": {"type": "string"}}}, 404: {"type": "string"}},
    )

    def delete(self, request, pk=None, *args, **kwargs):
        try:
            feature = Feature.objects.get(pk=pk)
        except Feature.DoesNotExist:
            return Response({"detail": "Feature not found."}, status=status.HTTP_404_NOT_FOUND)

        feature.delete()
        return Response({"detail": "Feature deleted."}, status=status.HTTP_204_NO_CONTENT)

class FeatureValueListAPIView(APIView):
    @extend_schema(
        request=FeatureValueSerializer,
        responses=FeatureValueSerializer,
        description="Get all Feature values"
    )
    def get(self, request, *args, **kwargs):
        feature_values = FeatureValue.objects.all()
        serializer = FeatureValueSerializer(feature_values, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class FeatureValueAPIView(APIView):
    @extend_schema(
        request=FeatureValueSerializer,
        responses=FeatureValueSerializer,
        description="Add Feature Value"
    )

    def post(self, request, *args, **kwargs):
        serializer = FeatureValueSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @extend_schema(
        operation_id="Retrieve Feature-value",
        description="Retrieve a single feature-value by its ID.",
        responses={200: FeatureValueSerializer, 404: {"type": "object", "properties": {"detail": {"type": "string"}}}},
    )
    def get(self, request, pk=None, *args, **kwargs):
        feature_name = request.query_params.get('feature')
        if pk:
            try:
                feature_value = FeatureValue.objects.get(pk=pk)
            except FeatureValue.DoesNotExist:
                return Response({"detail": "Feature value not found."}, status=status.HTTP_404_NOT_FOUND)
            serializer = FeatureValueSerializer(feature_value)
            return Response(serializer.data)
        elif feature_name:
            feature_values = FeatureValue.objects.filter(feature__name=feature_name)
        else:
            feature_values = FeatureValue.objects.all()
        serializer = FeatureValueSerializer(feature_values, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    @extend_schema(
        operation_id="Update Feature-value",
        description="Update a feature-value by its ID.",
        request=FeatureValue,
        responses={200: FeatureValue, 400: {"type": "object", "properties": {"detail": {"type": "string"}}}},
    )
    def put(self, request, pk=None, *args, **kwargs):
        try:
            feature_value = FeatureValue.objects.get(pk=pk)
        except FeatureValue.DoesNotExist:
            return Response({"detail": "Feature value not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = FeatureValueSerializer(feature_value, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        operation_id="Delete Feature-value",
        description="Delete a feature-value by its ID.",
        responses={204: {"type": "object", "properties": {"detail": {"type": "string"}}}, 404: {"type": "string"}},
    )
    def delete(self, request, pk=None, *args, **kwargs):
        try:
            feature_value = FeatureValue.objects.get(pk=pk)
        except FeatureValue.DoesNotExist:
            return Response({"detail": "Feature value not found."}, status=status.HTTP_404_NOT_FOUND)

        feature_value.delete()
        return Response({"detail": "Feature value deleted."}, status=status.HTTP_204_NO_CONTENT)

class ProductPerCategoryAPIView(APIView):
    """
    APIView for listing products by category name.
    """

    def get(self, request, category_name=None, *args, **kwargs):
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

class ProductFilterAPIView(APIView):
    @extend_schema(
        request=None,
        responses=ProductSerializer(many=True),
        description="Filter products by category and features.",
        parameters=[
            OpenApiParameter(
                name="category",
                type=int,
                location=OpenApiParameter.QUERY,
                description="Category ID to filter by",
                required=False,
            ),
            OpenApiParameter(
                name="features",
                type=str,
                location=OpenApiParameter.QUERY,
                description="List of features to filter by (e.g., '[{\"name\": \"color\", \"value\": \"red\"}]')",
                required=False,
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        category_id = request.query_params.get('category')
        features_param = request.query_params.get('features')

        queryset = Product.objects.all()

        if category_id:
            queryset = queryset.filter(category__id=category_id)

        if features_param:
            try:
                features_list = json.loads(features_param)
                for feature in features_list:
                    feature_name = feature.get('name')
                    feature_value = feature.get('value')
                    
                    if feature_name and feature_value:
                        queryset = queryset.filter(
                            features__feature__name=feature_name, 
                            features__value=feature_value
                        )
            except json.JSONDecodeError:
                return Response(
                    {"error": "Invalid JSON format for features"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
class ProductSortPriceAPIView(APIView):

    @extend_schema(
        request=None,  # No body for GET method
        responses=ProductSerializer(many=True),
        description="Sort products by maximum price in descending order.",
        parameters=[
            OpenApiParameter(
                name="order",
                type=str,
                location=OpenApiParameter.QUERY,
                description="The sort order. Use 'asc' for ascending or 'desc' for descending.",
                required=False,
                enum=["asc", "desc"],
                default="desc"
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        order = request.query_params.get('order', 'desc').lower()

        # Validate `order` parameter
        if order not in ['asc', 'desc']:
            return Response(
                {"error": "Invalid order value. Use 'asc' or 'desc'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Sort by price in descending order (maximum price first)
        if order == 'asc':
            sorted_products = Product.objects.all().order_by('price')
        else:
            sorted_products = Product.objects.all().order_by('-price')  # Descending

        serializer = ProductSerializer(sorted_products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProductSortByNameAPIView(APIView):
    """
    API to sort products by name.
    Use `?order=asc` or `?order=desc` for ascending or descending order.
    """

    @extend_schema(
        request=None,  # No body for GET method
        responses=ProductSerializer(many=True),
        description="Sort products by name in ascending or descending order.",
        parameters=[
            OpenApiParameter(
                name="order",
                type=str,
                location=OpenApiParameter.QUERY,
                description="The sort order. Use 'asc' for ascending or 'desc' for descending.",
                required=False,
                enum=["asc", "desc"],
                default="asc"
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        # Retrieve the 'order' query parameter
        order = request.query_params.get('order', 'asc').lower()

        # Validate `order` parameter
        if order not in ['asc', 'desc']:
            return Response(
                {"error": "Invalid order value. Use 'asc' or 'desc'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Case-insensitive sorting by name
        is_desc = order == 'desc'
        sorted_products = Product.objects.all().order_by(
            Lower('name').desc() if is_desc else Lower('name')
        )

        serializer = ProductSerializer(sorted_products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProductSearchAPIView(APIView):
    @extend_schema(
        request=None,  # No body for GET method
        responses=ProductSerializer(many=True),
        description="Search for products by a query string in their name.",
        parameters=[
            OpenApiParameter(
                name='query',
                type=str,
                location=OpenApiParameter.QUERY,
                description='The search query string to filter products by name.',
                required=True
            )
        ],
    )
    def get(self, request, *args, **kwargs):
        
        query = request.query_params.get("query", None)

        if not query:
            return Response({"error": "Query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Filter products based on the query
        products = Product.objects.filter(name__icontains=query)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    


class CommentCreateAPI(APIView):
    serializer_class = CommentCreateSerializer
      
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({
                'message': 'comment created succesfuly', 
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CommentRetriveView(APIView):
    serializer_class = CommentDetailSerializer
    
    def get(self, request, product_id, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"detail": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        comments = Comment.objects.filter(product=product)
        if not comments.exists():
            return Response({"detail": "No comments found for this product."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def delete(self, request, *args, **kwargs):
        if (not request.user.is_authenticated):
            return Response("user not authenticated", status=status.HTTP_401_UNAUTHORIZED)
        
        email = request.user.email
        user = User.objects.get(email=email)
        serializer = self.serializer_class(data = request.data)
        
        serializer.is_valid(raise_exception=True)
        
        if user.check_password(serializer.validated_data.get('password')):
            return Response("invalid password", status=status.HTTP_400_BAD_REQUEST)
        
        user.delete()
        return Response("user deleted successfully", status=status.HTTP_200_OK)

    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def patch(self, request, *args, **kwargs):
        try:
            email = request.user.email
            user = User.objects.get(email=email)
            serializer = self.serializer_class(user, data = request.data, partial=True)
        
            if serializer.is_valid():
                serializer.update(user, serializer.validated_data)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except User.DoesNotExist:
            return Response("user not found", status=status.HTTP_404_NOT_FOUND)