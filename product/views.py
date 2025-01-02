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
from rest_framework.permissions import IsAuthenticated
from .services import FavoritService , ProductService
from .permissions import IsAdminOrReadOnly
from drf_spectacular.types import OpenApiTypes
from django.http import QueryDict
import json
import logging
from  django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)

CACHE_TTL = getattr(settings, 'CACHE_TTL', 60 * 15)
class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class ProductListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        cache_key = f"product_list_{page}_{page_size}"

        print(f"Checking cache for key: {cache_key}")
        cached_data = cache.get(cache_key)
        print("Cached data:", cached_data)

        if cached_data is not None:
            print("Cache hit.")
            return Response(cached_data)

        print("Cache miss. Querying database.")
        queryset = Product.objects.all().order_by('-created_at')
        paginator = CustomPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        if paginated_queryset is None:
            print("Pagination failed.")
            return Response({"error": "Pagination failed"}, status=500)

        serializer = ProductSerializer(paginated_queryset, many=True, context={'request': request})
        response = paginator.get_paginated_response(serializer.data)

        print("Caching data for key:", cache_key)
        print("Data being cached:", response.data)

        cache.set(cache_key, response.data, timeout=CACHE_TTL)

        return response


class ProductAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [IsAdminOrReadOnly]
    @extend_schema(
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the product"},
                    "description": {"type": "string", "description": "Description of the product"},
                    "price": {"type": "number", "description": "Price of the product"},
                    "count_exist": {"type": "integer", "description": "Stock count for the product"},
                    "features": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "key": {"type": "string", "description": "Feature name"},
                                "value": {"type": "string", "description": "Feature value"}
                            }
                        }
                    },
                    "uploaded_images": {"type": "array", "items": {"type": "string", "format": "binary"}},
                    "category": {"type": "integer"}
                }
            }
        },
        responses=ProductSerializer,
        description="Create a new product with all supported fields.",
    )

    def post(self, request, *args, **kwargs):
        print("Raw Request Data:", request.data)
        features = request.data.get('features')
        print("Raw Features Field:", features)

        # Parse the features field if it's a stringified JSON array
        if isinstance(features, str):
            try:
                features = json.loads(features)  # Parse JSON string to Python list
                print("Parsed Features:", features)
            except json.JSONDecodeError:
                return Response(
                    {"features": ["Invalid JSON format for features."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Validate the features format
        if not isinstance(features, list):
            return Response(
                {"features": ["Features must be a list of dictionaries."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        for i, feature in enumerate(features):
            if not isinstance(feature, dict) or 'feature' not in feature or 'value' not in feature:
                return Response(
                    {"features": {i: "Each item must be a dictionary with 'feature' and 'value' keys."}},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Build a new mutable dictionary with parsed data
        data = request.data.dict() if isinstance(request.data, QueryDict) else request.data
        data.update(request.FILES)  # Include files in the data
        data['features'] = features  # Replace features with parsed list
        print("Formatted Data:", data)

        # Pass the formatted data to the serializer
        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        print("Serializer Errors:", serializer.errors)  # Debug serializer errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def get(self, request, pk=None, *args, **kwargs):
        """Retrieve a single product by ID."""
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product, context={'request': request})
        return Response(serializer.data)



    @extend_schema(
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the product"
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of the product",
                        "nullable": True
                    },
                    "price": {
                        "type": "number",
                        "description": "Price of the product"
                    },
                    "count_exist": {
                        "type": "integer",
                        "description": "Stock count for the product"
                    },
                    "features": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "feature": {"type": "string"},
                                "value": {"type": "string"}
                            }
                        },
                        "nullable": True
                    },
                    "uploaded_images": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "format": "binary"
                        },
                        "nullable": True
                    },
                    "primary_image_id": {
                        "type": "integer",
                        "nullable": True
                    },
                    "category": {
                        "type": "integer",
                        "nullable": True
                    }
                }
            }
        }
    )
    def patch(self, request, pk):
        """Partially update a product."""
        logger.info("PATCH request received with data: %s", request.data)

        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Handle features
        features = request.data.get('features')
        if features:
            if isinstance(features, str):
                try:
                    features = json.loads(features)
                except json.JSONDecodeError:
                    return Response(
                        {"features": ["Invalid JSON format for features."]},
                        status=status.HTTP_400_BAD_REQUEST,
                    )


        # Handle uploaded_images
        uploaded_images = request.FILES.getlist('uploaded_images')
        
        # Prepare data for serializer
        data = request.data.dict() if hasattr(request.data, 'dict') else request.data.copy()
        
        if features:
            data['features'] = features
        if uploaded_images:
            data['uploaded_images'] = uploaded_images

        # Validate and save
        serializer = ProductSerializer(product, data=data, partial=True)
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
    permission_classes = [IsAdminOrReadOnly]
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
    permission_classes = [IsAdminOrReadOnly]
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
    permission_classes = [IsAuthenticated]
    serializer_class = CommentCreateSerializer
      
    def post(self, request):
        # serializer = self.serializer_class(data=request.data)
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({
                'message': 'comment created succesfuly', 
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ShowAllCommentView(APIView):
    serializer_class = CommentDetailSerializer

    def get(self, request, *args, **kwargs):
        comments = Comment.objects.all()  # Fetch all comments
        serializer = self.serializer_class(comments, many=True)  # Serialize the comments
        return Response(serializer.data, status=status.HTTP_200_OK)  
    
    

class CommentRetriveView(APIView):
    serializer_class = CommentDetailSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get(self, request, comment_id, *args, **kwargs):
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({"detail": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, comment_id, *args, **kwargs):
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({"detail": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)

        if comment.user != request.user:
            return Response({"detail": "You do not have permission to delete this comment."}, status=status.HTTP_403_FORBIDDEN)

        comment.delete()
        return Response({"detail": "Comment deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, comment_id, *args, **kwargs):
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return Response({"detail": "Comment not found."}, status=status.HTTP_404_NOT_FOUND)

        if comment.user != request.user:
            return Response({"detail": "You do not have permission to edit this comment."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(comment, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)



class ProductCommentsView(APIView):
    serializer_class = CommentDetailSerializer

    def get(self, request, product_id, *args, **kwargs):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve all comments for the product
        comments = Comment.objects.filter(product=product)
        if not comments.exists():
            return Response({"detail": "No comments found for this product."}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the comments
        serializer = self.serializer_class(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class SimilarProductsView(APIView):
    serializer_class = ProductSerializer

    def get(self, request, product_id, *args, **kwargs):
        try:
            # Fetch the product to get its category
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        # Get up to 10 products in the same category, excluding the current product
        similar_products = Product.objects.filter(category=product.category).exclude(id=product_id)[:10]

        if not similar_products.exists():
            return Response({"detail": "No similar products found."}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the similar products
        serializer = self.serializer_class(similar_products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




class ProductImageDeleteView(APIView):
    permission_classes = [IsAdminOrReadOnly]
    def delete(self, request, product_pk, image_pk):

        try:

            product = Product.objects.get(pk=product_pk)
            

            image = product.images.get(pk=image_pk)
            

            if image.is_primary:
                remaining_images = product.images.exclude(pk=image_pk)
                if remaining_images.exists():
                    
                    remaining_images.first().is_primary = True
                    remaining_images.first().save()
            
            
            image.delete()
            
            return Response(
                {"detail": "Image deleted successfully."}, 
                status=status.HTTP_204_NO_CONTENT
            )
        
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        except ProductImage.DoesNotExist:
            return Response(
                {"detail": "Image not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )


class ProductImagePrimaryView(APIView):
    permission_classes = [IsAdminOrReadOnly]
    def post(self, request, product_pk, image_pk):

        try:
            
            product = Product.objects.get(pk=product_pk)
            
            
            image = product.images.get(pk=image_pk)
            
            
            product.images.update(is_primary=False)
            
            
            image.is_primary = True
            image.save()
            
            return Response(
                {"detail": "Primary image updated successfully."}, 
                status=status.HTTP_200_OK
            )
        
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        except ProductImage.DoesNotExist:
            return Response(
                {"detail": "Image not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )
class FavoriteAPI(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FavoriteSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    def get(self, requset):

        try:

            favorite_service = FavoritService(requset.user)
            favorites = favorite_service.get_favorites()

            serializer = ProductSerializer(
                [fav.product for fav in favorites],
                many=True,
                context={'request':requset}
            )
            return Response({
                'count': len(serializer.data),
                'favorites': serializer.data
            })
        
        except Exception as e:
            return Response(
                {'detail': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):

        try:
            serializer = self.serializer_class(data=request.data)
            if not serializer.is_valid() :
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
            product_id = serializer.validated_data.get('product_id')
            try:
            
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response(
                    {'detail':'Product not found'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            favorite_service = FavoritService(request.user)

            try:
                favorite = favorite_service.add_to_favorites(product)

                return Response(
                    ProductSerializer(product, context={'request': request}).data,
                    status=status.HTTP_201_CREATED
                )
            except ValidationError as ve:
                return Response(
                    {'detail':str(ve)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        

        except Exception as e:
            return Response(
                {'detail':str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    @extend_schema(
        description="Delete a product from favorites.",
        parameters=[
            OpenApiParameter(
                name='product_id',  # Name of the parameter
                type=int,            # Type of the parameter (e.g., integer)
                location=OpenApiParameter.QUERY,  # Location in query parameters
                description="ID of the product to remove from favorites."
            ),
        ]
    )
    def delete(self, request):

        try:
            product_id = request.query_params.get('product_id')

            if not product_id:
                return Response(
                    {'detail': 'Product ID is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response(
                    {'detail': 'Product not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            favorite_service = FavoritService(request.user)
            
            removed = favorite_service.remove_from_favorites(product)
            
            if removed:
                return Response(
                    {'detail': 'Product removed from favorites'}, 
                    status=status.HTTP_204_NO_CONTENT
                )
            
            return Response(
                {'detail': 'Product not in favorites'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        except Exception as e:
            return Response(
                {'detail': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 

class FavoriteToggleAPIView(APIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    def post(self, request):

        try:
            
            serializer = self.serializer_class(data=request.data)
            if not serializer.is_valid():
                return Response(
                    serializer.errors, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            
            product_id = serializer.validated_data.get('product_id')
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response(
                    {'detail': 'Product not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            
            favorite_service = FavoritService(request.user)
            
            
            is_now_favorite = favorite_service.toggle_favorite(product)
            
            return Response({
                'product': ProductSerializer(product, context={'request': request}).data,
                'is_favorite': is_now_favorite
            })
        
        except Exception as e:
            return Response(
                {'detail': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


## با کوئری پارام و ایدی کتگوری


# class ProductFilterAndSortAPIView(APIView):
#     @extend_schema(
#         request=None,
#         responses=ProductSerializer(many=True),
#         description="Filter and sort products by category, features, name (optional), and price.",
#         parameters=[
#             OpenApiParameter(
#                 name="category",
#                 type=int,
#                 location=OpenApiParameter.QUERY,
#                 description="Category ID to filter by",
#                 required=False,
#             ),
#             OpenApiParameter(
#                 name="features",
#                 type=str,
#                 location=OpenApiParameter.QUERY,
#                 description="List of features to filter by (e.g., '[{\"name\": \"color\", \"value\": \"red\"}]')."
#                             "Direct fields like 'price' and 'count_exist' can also be filtered.",
#                 required=False,
#             ),
#             OpenApiParameter(
#                 name="order",
#                 type=str,
#                 location=OpenApiParameter.QUERY,
#                 description="The sort order for product names. Use 'asc' for ascending or 'desc' for descending.",
#                 required=False,
#                 enum=["asc", "desc"],
#             ),
#             OpenApiParameter(
#                 name="price_order",
#                 type=str,
#                 location=OpenApiParameter.QUERY,
#                 description="The sort order for price. Use 'asc' for ascending or 'desc' for descending.",
#                 required=False,
#                 enum=["asc", "desc"],
#             ),
#         ]
#     )
#     def get(self, request, *args, **kwargs):
#         category_id = request.query_params.get('category')
#         features_param = request.query_params.get('features')
#         order = request.query_params.get('order', None)
#         price_order = request.query_params.get('price_order', None)

#         # Start with all products
#         queryset = Product.objects.all()

#         # Filter by category
#         if category_id:
#             queryset = queryset.filter(category__id=category_id)

#         # Filter by features or direct fields
#         if features_param:
#             try:
#                 features_list = json.loads(features_param)
#                 for feature in features_list:
#                     feature_name = feature.get('name')
#                     feature_value = feature.get('value')
                    
#                     if not feature_name or not feature_value:
#                         continue
                    
#                     # Handle price feature (filter products less than the specified price)
#                     if feature_name == "price":
#                         try:
#                             price_value = float(feature_value)
#                             queryset = queryset.filter(price__lt=price_value)  # Filter for price less than the given value
#                         except ValueError:
#                             return Response(
#                                 {"error": "Invalid value for price, should be a number."},
#                                 status=status.HTTP_400_BAD_REQUEST
#                             )
#                     else:
#                         # Handle other features in FeatureValue model
#                         queryset = queryset.filter(
#                             features__feature__name=feature_name,
#                             features__value=feature_value
#                         )
#             except json.JSONDecodeError:
#                 return Response(
#                     {"error": "Invalid JSON format for features"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#         # Optional: Sort by name if 'order' is specified
#         if order:
#             if order not in ['asc', 'desc']:
#                 return Response(
#                     {"error": "Invalid order value. Use 'asc' or 'desc'."},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#             is_desc_name = order == 'desc'
#             queryset = queryset.order_by(
#                 Lower('name').desc() if is_desc_name else Lower('name')
#             )

#         # Sort by price if `price_order` is specified
#         if price_order:
#             if price_order not in ['asc', 'desc']:
#                 return Response(
#                     {"error": "Invalid price_order value. Use 'asc' or 'desc'."},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#             is_desc_price = price_order == 'desc'
#             queryset = queryset.order_by(
#                 '-price' if is_desc_price else 'price'
#             )

#         # Serialize and return the results
#         serializer = ProductSerializer(queryset, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)



## با کوئری پارام و اسم کتگوری


# class ProductFilterAndSortAPIView(APIView):
#     @extend_schema(
#         request=None,
#         responses=ProductSerializer(many=True),
#         description="Filter and sort products by category name, features, name (optional), and price.",
#         parameters=[
#             OpenApiParameter(
#                 name="category",
#                 type=str,
#                 location=OpenApiParameter.QUERY,
#                 description="Category name to filter by",
#                 required=False,
#             ),
#             OpenApiParameter(
#                 name="features",
#                 type=str,
#                 location=OpenApiParameter.QUERY,
#                 description="List of features to filter by (e.g., '[{\"name\": \"color\", \"value\": \"red\"}]')."
#                             "Direct fields like 'price' and 'count_exist' can also be filtered.",
#                 required=False,
#             ),
#             OpenApiParameter(
#                 name="order",
#                 type=str,
#                 location=OpenApiParameter.QUERY,
#                 description="The sort order for product names. Use 'asc' for ascending or 'desc' for descending.",
#                 required=False,
#                 enum=["asc", "desc"],
#             ),
#             OpenApiParameter(
#                 name="price_order",
#                 type=str,
#                 location=OpenApiParameter.QUERY,
#                 description="The sort order for price. Use 'asc' for ascending or 'desc' for descending.",
#                 required=False,
#                 enum=["asc", "desc"],
#             ),
#         ]
#     )
#     def get(self, request, *args, **kwargs):
#         category_name = request.query_params.get('category')
#         features_param = request.query_params.get('features')
#         order = request.query_params.get('order', None)
#         price_order = request.query_params.get('price_order', None)

#         # Start with all products
#         queryset = Product.objects.all()

#         # Filter by category name
#         if category_name:
#             queryset = queryset.filter(category__name__iexact=category_name)

#         # Filter by features or direct fields
#         if features_param:
#             try:
#                 features_list = json.loads(features_param)
#                 for feature in features_list:
#                     feature_name = feature.get('name')
#                     feature_value = feature.get('value')
                    
#                     if not feature_name or not feature_value:
#                         continue
                    
#                     # Handle price feature (filter products less than the specified price)
#                     if feature_name == "price":
#                         try:
#                             price_value = float(feature_value)
#                             queryset = queryset.filter(price__lt=price_value)  # Filter for price less than the given value
#                         except ValueError:
#                             return Response(
#                                 {"error": "Invalid value for price, should be a number."},
#                                 status=status.HTTP_400_BAD_REQUEST
#                             )
#                     else:
#                         # Handle other features in FeatureValue model
#                         queryset = queryset.filter(
#                             features__feature__name=feature_name,
#                             features__value=feature_value
#                         )
#             except json.JSONDecodeError:
#                 return Response(
#                     {"error": "Invalid JSON format for features"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#         # Optional: Sort by name if 'order' is specified
#         if order:
#             if order not in ['asc', 'desc']:
#                 return Response(
#                     {"error": "Invalid order value. Use 'asc' or 'desc'."},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#             is_desc_name = order == 'desc'
#             queryset = queryset.order_by(
#                 Lower('name').desc() if is_desc_name else Lower('name')
#             )

#         # Sort by price if `price_order` is specified
#         if price_order:
#             if price_order not in ['asc', 'desc']:
#                 return Response(
#                     {"error": "Invalid price_order value. Use 'asc' or 'desc'."},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#             is_desc_price = price_order == 'desc'
#             queryset = queryset.order_by(
#                 '-price' if is_desc_price else 'price'
#             )

#         # Serialize and return the results
#         serializer = ProductSerializer(queryset, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)






####### با جیسون و اسم کتگوری

class ProductFilterAndSortAPIView(APIView):
    @extend_schema(
        request=OpenApiTypes.OBJECT,
        responses=ProductSerializer(many=True),
        description="Filter and sort products by category name, features, name (optional), and price.",
        examples=[
            OpenApiExample(
                "Example Request",
                value={
                    "category": "Electronics",
                    "features": [{"name": "color", "value": "red"}],
                    "order": "asc",
                    "price_order": "desc"
                }
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        category_name = request.data.get('category')
        features_param = request.data.get('features')
        order = request.data.get('order', None)
        price_order = request.data.get('price_order', None)

        # Start with all products
        queryset = Product.objects.all()

        # Filter by category name
        if category_name:
            queryset = queryset.filter(category__name__iexact=category_name)

        # Filter by features or direct fields
        if features_param:
            try:
                for feature in features_param:
                    feature_name = feature.get('name')
                    feature_value = feature.get('value')
                    
                    if not feature_name or not feature_value:
                        continue
                    
                    # Handle price feature (filter products less than the specified price)
                    if feature_name == "price":
                        try:
                            price_value = float(feature_value)
                            queryset = queryset.filter(price__lt=price_value)  # Filter for price less than the given value
                        except ValueError:
                            return Response(
                                {"error": "Invalid value for price, should be a number."},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                    else:
                        # Handle other features in FeatureValue model
                        queryset = queryset.filter(
                            features__feature__name=feature_name,
                            features__value=feature_value
                        )
            except (TypeError, ValueError):
                return Response(
                    {"error": "Invalid format for features. Expected a list of objects with 'name' and 'value'."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Optional: Sort by name if 'order' is specified
        if order:
            if order not in ['asc', 'desc']:
                return Response(
                    {"error": "Invalid order value. Use 'asc' or 'desc'."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            is_desc_name = order == 'desc'
            queryset = queryset.order_by(
                Lower('name').desc() if is_desc_name else Lower('name')
            )

        # Sort by price if `price_order` is specified
        if price_order:
            if price_order not in ['asc', 'desc']:
                return Response(
                    {"error": "Invalid price_order value. Use 'asc' or 'desc'."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            is_desc_price = price_order == 'desc'
            queryset = queryset.order_by(
                '-price' if is_desc_price else 'price'
            )

        # Serialize and return the results
        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
class MostSoldProductsView(APIView):
    def get(self, request):
        products = ProductService.get_most_sold_products()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
