from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from user import permissions
from .serializers import AdminOrderStatusUpdateSerializer, OrderSerializer, CreateOrderSerializer, PaymentSerializer
from Order import serializers
from django.core.exceptions import ValidationError
from rest_framework import permissions
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from .models import Order
from rest_framework.pagination import PageNumberPagination




class OrderListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List Orders",
        description="Retrieve a list of all orders for the authenticated user.",
        responses={200: OrderSerializer(many=True)}
    )
    def get(self, request):
        try:
            orders = Order.objects.filter(user=request.user)
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
    @extend_schema(
        summary="Create an Order",
        description="Create a new order from the authenticated user's cart.",
        request=CreateOrderSerializer,
        responses={201: OrderSerializer, 400: "Validation Error"}
    )
    def post(self, request):
        try:
            serializer = CreateOrderSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                print("fvrv")

                order = serializer.save()
                print("fvrv")

                return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, order_id, user):
        try:
            return Order.objects.get(id=order_id, user=user)
        except Order.DoesNotExist:
            return None
        
    @extend_schema(
        summary="Retrieve Order Details",
        description="Get detailed information about a specific order.",
        responses={200: OrderSerializer, 404: "Order not found"}
    )
    def get(self, request, order_id):
        order = self.get_object(order_id, request.user)
        if not order:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Delete an Order",
        description="Delete a specific order owned by the authenticated user.",
        responses={204: "Order deleted", 404: "Order not found"}
    )
    def delete(self, request, order_id):
        order = self.get_object(order_id, request.user)
        if not order:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        order.delete()
        return Response({"message": "Order deleted"}, status=status.HTTP_204_NO_CONTENT)


class WalletPaymentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Pay for an Order",
        description="Make a payment for a specific order using the authenticated user's wallet.",
        request=PaymentSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "order_id": {"type": "integer"},
                    "payment_status": {"type": "string"},
                    "remaining_balance": {"type": "number"},
                }
            },
            400: "Payment error or validation error"
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                print("jon baba")
                order = serializer.process_payment(serializer.validated_data)
                print("va?")
                return Response(
                    {
                        "message": "Payment successful",
                        "order_id": order.id,
                        "payment_status": order.payment_status,
                        "remaining_balance": order.user.wallet.balance
                    },
                    status=status.HTTP_200_OK
                )
            except serializers.ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class IsAdminUser(permissions.BasePermission):
    permission_classes = [IsAuthenticated]

    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class AdminOrderStatusUpdateView(APIView):
    permission_classes = [IsAdminUser]
    
    @extend_schema(
        summary="Update Order Status",
        description="Allows admin users to update the status of an order.",
        request=AdminOrderStatusUpdateSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "order_id": {"type": "integer"},
                }
            },
            400: "Validation Error"
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = AdminOrderStatusUpdateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                result = serializer.update_status(serializer.validated_data)
                return Response(result, status=status.HTTP_200_OK)
            except serializers.ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserOrderHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
        summary="Get User Order History",
        description="Retrieve a paginated list of the authenticated user's order history.",
        responses={
            200: OrderSerializer(many=True),
        },
    )
    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')

        paginator = PageNumberPagination()
        paginator.page_size = 10 
        paginated_orders = paginator.paginate_queryset(orders, request)

        serializer = OrderSerializer(paginated_orders, many=True)

        return paginator.get_paginated_response(serializer.data)
