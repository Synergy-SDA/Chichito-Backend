
from rest_framework import permissions
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated

class IsAdminUser(permissions.BasePermission):
    permission_classes = [IsAuthenticated]
    def has_permission(self, request, view):
        print(request.user.is_staff)
        return request.user and request.user.is_staff
