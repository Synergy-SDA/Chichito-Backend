from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Category
from .serializers import *
from .permissions import IsOwnerOrReadOnly

class CategoryListCreateAPIView(APIView):
    serializer_class = CategoryCreateSerializer
    permission_classes = [IsOwnerOrReadOnly]
    def get(self, request):
        categories = Category.objects.all()
        serializer = self.serializer_class(categories, many=True)  # Serialize the queryset
        return Response(serializer.data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)  # Use `serializer_class` for consistency
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryDetailAPIView(APIView):
    serializer_class = CategoryDetailSerializer
    permission_classes = [IsOwnerOrReadOnly]    
    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return None

    def get(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(category)
        return Response(serializer.data)

    def put(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        category = self.get_object(pk)
        if not category:
            return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

        category.delete()
        return Response({"detail": "Category deleted."}, status=status.HTTP_204_NO_CONTENT)
