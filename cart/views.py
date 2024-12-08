from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .services import CartService
from .serializers import CartSerializer, CartItemSerializer
from rest_framework.exceptions import ValidationError


class CartAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        cart = CartService.get_or_create_cart(request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


    def post(self, request):
        cart = CartService.get_or_create_cart(request.user)
        product_id = request.data.get('product_id')
        print("sss",product_id)
        quantity = request.data.get('quantity', 1)

        try:
            cart_item = CartService.add_item(cart, product_id, quantity)
            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Update item quantity in the cart",
        parameters=[
            OpenApiParameter("product_id", int, description="ID of the product"),
            OpenApiParameter("quantity", int, description="New quantity"),
        ],
        request=None,
        responses={200: CartItemSerializer, 400: "Validation Error"},
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
        parameters=[
            OpenApiParameter("product_id", int, description="ID of the product"),
        ],
        request=None,
        responses={204: None, 400: "Validation Error"},
    )
    def delete(self, request):
        cart = CartService.get_or_create_cart(request.user)
        product_id = request.data.get('product_id')

        try:
            CartService.remove_item(cart, product_id)
            return Response({'message': 'Item removed successfully.'}, status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
