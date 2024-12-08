from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .services import CartService
from .serializers import CartSerializer, CartItemSerializer
from rest_framework.exceptions import ValidationError


from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

class CartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Retrieve the user's cart",
        description="Returns the cart associated with the authenticated user, creating it if it doesn't already exist.",
        responses={
            200: CartSerializer,
        },
    )
    def get(self, request):
        cart = CartService.get_or_create_cart(request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @extend_schema(
        summary="Add an item to the cart",
        description="Adds a product to the user's cart. If the product already exists in the cart, its quantity is updated.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "integer", "description": "ID of the product"},
                    "quantity": {
                        "type": "integer",
                        "description": "Quantity of the product to add (default is 1)",
                        "example": 1,
                    },
                },
                "required": ["product_id"],
            }
        },
        responses={
            201: CartItemSerializer,
            400: "Validation Error",
        },
    )
    def post(self, request):
        cart = CartService.get_or_create_cart(request.user)
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        try:
            cart_item = CartService.add_item(cart, product_id, quantity)
            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Update an item in the cart",
        description="Updates the quantity of a product in the user's cart.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "integer", "description": "ID of the product"},
                    "quantity": {
                        "type": "integer",
                        "description": "New quantity for the product",
                        "example": 2,
                    },
                },
                "required": ["product_id", "quantity"],
            }
        },
        responses={
            200: CartItemSerializer,
            400: "Validation Error",
        },
    )
    def put(self, request):
        cart = CartService.get_or_create_cart(request.user)
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')

        try:
            cart_item = CartService.update_item(cart, product_id, quantity)
            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Remove an item from the cart",
        description="Removes a product from the user's cart by specifying its product ID.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "integer", "description": "ID of the product to remove"},
                },
                "required": ["product_id"],
            }
        },
        responses={
            204: None,
            400: "Validation Error",
        },
    )
    def delete(self, request):
        cart = CartService.get_or_create_cart(request.user)
        product_id = request.data.get('product_id')

        try:
            CartService.remove_item(cart, product_id)
            return Response({'message': 'Item removed successfully.'}, status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

