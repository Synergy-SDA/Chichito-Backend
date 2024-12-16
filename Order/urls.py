from django.urls import path
from .views import AdminOrderStatusUpdateView, OrderListCreateView, OrderDetailView, UserOrderHistoryAPIView, WalletPaymentAPIView 

urlpatterns = [
    path('orders/', OrderListCreateView.as_view(), name='order-list-create'),
    path('orders/<int:order_id>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/pay/', WalletPaymentAPIView.as_view(), name='pay-order'),
    path('admin/orders/update-status/', AdminOrderStatusUpdateView.as_view(), name='admin-order-status-update'),
    path('orders/history/', UserOrderHistoryAPIView.as_view(), name='order-history'),
]
