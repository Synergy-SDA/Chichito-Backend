from rest_framework import serializers
from .models import *
from category.serializers import *


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:     
        model = Feature
        fields = ['id', 'name']
class FeatureValueSerializer(serializers.ModelSerializer):
    feature = serializers.CharField()
    class Meta:
        model = FeatureValue
        fields = ['value', 'feature']   
    def validate_feature(self, value):
        try:
            feature = Feature.objects.get(name__iexact=value)
        except Feature.DoesNotExist:
            raise serializers.ValidationError(f"Feature with name '{value}' does not exist.")
        return feature  
    def validate(self, data):
        feature = self.validate_feature(data.get('feature'))  
        value = data.get('value')

        if FeatureValue.objects.filter(feature=feature,  value__iexact=value).exists():
            raise serializers.ValidationError(
                {"detail": f"A FeatureValue with feature '{feature.name}' and value '{value}' already exists."}
            )
        data['feature'] = feature
        return data
    def create(self, validated_data):
        feature = validated_data.pop('feature')
        return FeatureValue.objects.create(feature=feature, **validated_data)   

class ProductSerializer(serializers.ModelSerializer):
    features = serializers.ListField(
        child=serializers.DictField(),  # Accept a list of dictionaries
        write_only=True
    )
    product_features = serializers.SerializerMethodField(read_only=True)
    category = CategorySerializer()

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'price',
            'count_exist',
            'is_available',
            'created_at',
            'updated_at',
            'features',# write-only field for create/update
            'category',
            'product_features',
        ]
    def get_product_features(self, obj):
        return [
            {
                'feature': feature_value.feature.name, 
                'value': feature_value.value
            } 
            for feature_value in obj.features.all()
        ]

    def create(self, validated_data):
        features_data = validated_data.pop('features', [])
        category_data = validated_data.pop('category', None)

        # Handle category creation or association
        category = None
        if category_data:
            category, _ = Category.objects.get_or_create(**category_data)

        # Create the product
        product = Product.objects.create(category=category, **validated_data)

        # Process feature values
        for feature_data in features_data:
            # Extract the key-value pair
            for key, value in feature_data.items():
                # Get or create the feature
                feature, _ = Feature.objects.get_or_create(name=key)
                # Create or retrieve the feature value
                feature_value, _ = FeatureValue.objects.get_or_create(
                    feature=feature,
                    value=value
                )
                # Associate the feature value with the product
                product.features.add(feature_value)

        return product


    def update(self, instance, validated_data):
        features_data = validated_data.pop('features', [])
        category_data = validated_data.pop('category', None)

        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update category
        if category_data:
            category, _ = Category.objects.get_or_create(**category_data)
            instance.category = category

        instance.save()

        # Update feature values
        if features_data:
            instance.features.clear()  # Remove existing features
            for feature_data in features_data:
                feature_name = feature_data.get('feature')
                value = feature_data.get('value')

                # Find or create FeatureValue
                try:
                    feature_value = FeatureValue.objects.get(
                        feature__name__iexact=feature_name,
                        value__iexact=value
                    )
                except FeatureValue.DoesNotExist:
                    # Create feature if it doesn't exist
                    feature, _ = Feature.objects.get_or_create(name=feature_name)
                    feature_value = FeatureValue.objects.create(feature=feature, value=value)

                # Add feature value to the product
                instance.features.add(feature_value)

        return instance

