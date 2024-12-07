from rest_framework import serializers
from .models import Category
from rest_framework import serializers
from .models import Category
from django.utils import timezone
import datetime

class CategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'description', 'parent']

    def validate(self, attrs):
        name = attrs.get('name')
        parent = attrs.get('parent')

        # Check if a category with the same name already exists
        if Category.objects.filter(name=name).exists():
            raise serializers.ValidationError("A category with this name already exists.")

        # Prevent cyclic relationships if a parent category is specified
        if parent and parent.id == self.instance.id if self.instance else False:
            raise serializers.ValidationError("A category cannot be its own parent.")

        # Optional: Validate that the parent is valid if needed
        if parent and not Category.objects.filter(id=parent.id).exists():
            raise serializers.ValidationError("The specified parent category does not exist.")

        return attrs

    def create(self, validated_data):
        # Create and return a new Category instance
        category = Category.objects.create(**validated_data)
        return category



class CategoryDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'parent']

    def validate(self, attrs):
        """Optional: Add custom validation if required."""
        parent = attrs.get('parent')

        # Prevent cyclic relationships
        if parent and parent.id == self.instance.id if self.instance else False:
            raise serializers.ValidationError("A category cannot be its own parent.")

        return attrs
