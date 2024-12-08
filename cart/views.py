from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.exceptions import ValidationError
from .services import CartService
from .serializers import CartSerializer, CartItemSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import GiftWrap
from .serializers import GiftWrapSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter

class CartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Add an item to the cart",
        description="Adds a product to the user's cart with optional gift wrap and message.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "integer", "description": "ID of the product"},
                    "quantity": {"type": "integer", "description": "Quantity of the product to add (default is 1)", "example": 1},
                    "gift_wrap_id": {"type": "integer", "description": "ID of the selected gift wrap (optional)"},
                    "gift_wrap_message": {"type": "string", "description": "Personalized message for the gift wrap (optional)", "example": "Happy Birthday!"}
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
        gift_wrap_id = request.data.get('gift_wrap_id')
        gift_wrap_message = request.data.get('gift_wrap_message')

        try:
            cart_item = CartService.add_item(cart, product_id, quantity, gift_wrap_id, gift_wrap_message)
            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Update an item in the cart",
        description="Updates the quantity and gift wrap details of a product in the user's cart.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "integer", "description": "ID of the product"},
                    "quantity": {"type": "integer", "description": "New quantity for the product", "example": 2},
                    "gift_wrap_id": {"type": "integer", "description": "ID of the selected gift wrap (optional)"},
                    "gift_wrap_message": {"type": "string", "description": "Personalized message for the gift wrap (optional)", "example": "Happy Birthday!"}
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
        gift_wrap_id = request.data.get('gift_wrap_id')
        gift_wrap_message = request.data.get('gift_wrap_message')

        try:
            cart_item = CartService.update_item(cart, product_id, quantity, gift_wrap_id, gift_wrap_message)
            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GiftWrapAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Retrieve list of gift wraps",
        description="Returns a list of all available gift wraps.",
        responses={
            200: GiftWrapSerializer(many=True),
        },
    )
    def get(self, request, *args, **kwargs):
        gift_wraps = GiftWrap.objects.all()
        serializer = GiftWrapSerializer(gift_wraps, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Create a new gift wrap",
        description="Creates a new gift wrap by providing necessary details such as name, description, and price.",
        request=GiftWrapSerializer,
        responses={
            201: GiftWrapSerializer,
            400: "Validation Error",
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = GiftWrapSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Update an existing gift wrap",
        description="Updates the details of an existing gift wrap. You must provide the ID of the gift wrap to be updated.",
        request=GiftWrapSerializer,
        responses={
            200: GiftWrapSerializer,
            400: "Validation Error",
            404: "Gift wrap not found",
        },
        parameters=[
            OpenApiParameter("pk", int, description="ID of the gift wrap to update", required=True)
        ]
    )
    def put(self, request, *args, **kwargs):
        gift_wrap = GiftWrap.objects.filter(id=kwargs['pk']).first()
        if not gift_wrap:
            raise ValidationError("Gift wrap not found.")
        
        serializer = GiftWrapSerializer(gift_wrap, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete a gift wrap",
        description="Deletes a gift wrap by its ID.",
        responses={
            204: "Gift wrap deleted successfully.",
            400: "Validation Error",
            404: "Gift wrap not found",
        },
        parameters=[
            OpenApiParameter("pk", int, description="ID of the gift wrap to delete", required=True)
        ]
    )
    def delete(self, request, *args, **kwargs):
        gift_wrap = GiftWrap.objects.filter(id=kwargs['pk']).first()
        if gift_wrap:
            gift_wrap.delete()
            return Response({"message": "Gift wrap deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        raise ValidationError("Gift wrap not found.")

