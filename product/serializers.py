from rest_framework import serializers
from .models import *
from category.serializers import *
import json
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id','image','is_primary','created_at']
        extra_kwargs = {'image': {'required': False},
                        'is_primary': {'required': False},
                        }

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
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        required=False,
        allow_null=True
    )
    category_details = CategoryDetailSerializer(source='category', read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    is_liked = serializers.SerializerMethodField()
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
            'category_details',
            'product_features',
            'images',
            'uploaded_images',
            'is_liked'
            ]
    def to_internal_value(self, data):
        print("to_internal_value: Full Data", data)  # Log the full input data

        features = data.get('features', [])
        print("to_internal_value: Raw Features", features)  # Log raw features

        # Validate features explicitly
        if not isinstance(features, list):
            raise serializers.ValidationError({"features": "Expected a list of dictionaries."})

        for i, feature in enumerate(features):
            if not isinstance(feature, dict):
                raise serializers.ValidationError({
                    "features": {i: f"Expected a dictionary but got type '{type(feature).__name__}'."}
                })
            if 'feature' not in feature or 'value' not in feature:
                raise serializers.ValidationError({
                    "features": {i: "Each dictionary must contain 'feature' and 'value'."}
                })

        return super().to_internal_value(data)
    def validate_features(self, value):
        print("Inside validate_features. Received value:", value)  # Debug value received

        # Ensure it is a list
        if not isinstance(value, list):
            raise serializers.ValidationError("Features must be a list of dictionaries.")

        # Validate each dictionary in the list
        for i, item in enumerate(value):
            print(f"Validating feature {i}:", item)  # Debug each feature item
            if not isinstance(item, dict):
                raise serializers.ValidationError(f"Expected a dictionary of items but got {type(item).__name__}.")
            if 'feature' not in item or 'value' not in item:
                raise serializers.ValidationError(
                    {i: "Each dictionary must contain 'feature' and 'value'."}
                )
        return value

    def get_product_features(self, obj):
        return [
            {
                'feature': feature_value.feature.name, 
                'value': feature_value.value
            } 
            for feature_value in obj.features.all()
        ]
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return FavoritProduct.objects.filter(user=request.user, product=obj).exists()
        return False

    def create(self, validated_data):
        features_data = validated_data.pop('features', [])
        category = validated_data.pop('category', None)
        uploaded_images = validated_data.pop('uploaded_images', [])
    # Handle category creation or association
        if isinstance(category, dict):
        # If category is passed as a dictionary, create or get the category
            category, _ = Category.objects.get_or_create(**category)

        product = Product.objects.create(category=category, **validated_data)

        # if features_data:

        feature_values = []
        for feature_data in features_data:
            # Use 'feature' and 'value' instead of 'key' and 'value'
            feature_name = feature_data.get('feature')  # Extract 'feature'
            feature_value_text = feature_data.get('value')

            if feature_name and feature_value_text:
                # Get or create the feature
                feature, _ = Feature.objects.get_or_create(name=feature_name)

                # Get or create the feature value
                feature_value, _ = FeatureValue.objects.get_or_create(
                    feature=feature,
                    value=feature_value_text
                )

                # Collect the feature values to add in bulk
                feature_values.append(feature_value)
            # Add all feature values to the product in a single operation
            product.features.add(*feature_values)
        
        if uploaded_images:
            ProductImage.objects.bulk_create([
                ProductImage(
                    product=product,
                    image=image,
                    is_primary=(i==0))
                    for i, image in enumerate(uploaded_images)
            ])  

        return product

    def update(self, instance, validated_data):
        features_data = validated_data.pop('features', [])
        category = validated_data.pop('category', None)
        uploaded_images = validated_data.pop('uploaded_images', [])
        
        # Update basic product fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Handle category update
        if category:
            if isinstance(category, dict):
                category, _ = Category.objects.get_or_create(**category)
            instance.category = category

        instance.save()

        # Update product features
        if features_data:
            # Clear existing features
            instance.features.clear()

            # Add new features
            feature_values = []
            for feature_data in features_data:
                feature_name = feature_data.get('feature')
                feature_value_text = feature_data.get('value')

                # Get or create the feature
                feature, _ = Feature.objects.get_or_create(name=feature_name)

                # Get or create the feature value
                feature_value, _ = FeatureValue.objects.get_or_create(
                    feature=feature,
                    value=feature_value_text
                )

                feature_values.append(feature_value)

            instance.features.add(*feature_values)

        # Handle image update - append new images without deleting existing ones
        if uploaded_images:
            # Determine the next primary status based on existing images
            existing_primary = instance.images.filter(is_primary=True).exists()

            new_images = []
            for i, image in enumerate(uploaded_images):
                is_primary = not existing_primary and i == 0
                new_images.append(
                    ProductImage(
                        product=instance,
                        image=image,
                        is_primary=is_primary
                    )
                )

            ProductImage.objects.bulk_create(new_images)

        return instance




class CommentCreateSerializer(serializers.ModelSerializer):
    rate = serializers.ChoiceField(choices=Comment.RatingChoices.choices)

    class Meta:
        model = Comment
        fields = ['user' ,'product', 'content', 'rate']
        read_only_fields = ['user'] 

    def validate(self, attrs):
        user = attrs.get('user')
        product = attrs.get('product')
        if not Product.objects.filter(id=product.id).exists():
            raise serializers.ValidationError({'product': 'Product does not exist.'})

        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return Comment.objects.create(**validated_data)
    
    
    

class CommentDetailSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['user', 'product', 'content', 'rate', 'first_name']
        read_only_fields = ['user']

    def get_first_name(self, obj):
        return obj.user.first_name

    def update(self, instance, validated_data):
        instance.content = validated_data.get('content', instance.content)
        instance.rate = validated_data.get('rate', instance.rate)

        instance.save()
        return instance

    
class FavoriteSerializer(serializers.Serializer):

    product_id = serializers.IntegerField()

    def validate_product_id(self, value):

        try:
            Product.objects.get(id=value)
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product does not exist")
    


        


    