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
        child=serializers.DictField(),
        write_only=True,
        required=False,
        allow_empty=True,
        allow_null=True
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
        child=serializers.FileField(
            allow_empty_file=True,
            use_url=False
        ),
        write_only=True,
        required=False,
        allow_empty=True,
        allow_null=True
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
            'features',
            'category',
            'category_details',
            'product_features',
            'images',
            'uploaded_images',
            'is_liked'
        ]

    def to_internal_value(self, data):
        data = data.copy() if hasattr(data, 'copy') else data.dict() if hasattr(data, 'dict') else data

        # Helper function to check if value represents null
        def is_null_value(value):
            return value in [None, 'null', 'None', '', [], 'undefined']
        
        if 'primary_image_id' in data:
            if is_null_value(data['primary_image_id']):
                data['primary_image_id'] = None
            elif isinstance(data['primary_image_id'], str):
                try:
                    if not is_null_value(data['primary_image_id']):
                        data['primary_image_id'] = int(data['primary_image_id'])
                except ValueError:
                    raise serializers.ValidationError({
                        'primary_image_id': 'A valid integer is required.'
                    })
        # Handle features field
        if 'features' in data:
            features = data['features']
            if is_null_value(features):
                data['features'] = None
            elif isinstance(features, str):
                if features.lower() == 'null':
                    data['features'] = None
                else:
                    try:
                        features = json.loads(features)
                        if not isinstance(features, list):
                            raise serializers.ValidationError({
                                'features': 'Expected a list of dictionaries.'
                            })
                        data['features'] = features
                    except json.JSONDecodeError:
                        raise serializers.ValidationError({
                            'features': 'Invalid JSON format for features.'
                        })



        # Handle uploaded_images
        if 'uploaded_images' in data:
            images = data['uploaded_images']
            if is_null_value(images):
                data['uploaded_images'] = None
            elif isinstance(images, str):
                if images.lower() == 'null':
                    data['uploaded_images'] = None
                elif not isinstance(images, list):
                    data['uploaded_images'] = [images]

        return super().to_internal_value(data)

    def validate_features(self, value):
        if not value:
            return value

        for i, item in enumerate(value):
            if not isinstance(item, dict):
                raise serializers.ValidationError(
                    f"Item {i}: Expected a dictionary but got {type(item).__name__}."
                )
            if 'feature' not in item or 'value' not in item:
                raise serializers.ValidationError(
                    f"Item {i}: Must contain 'feature' and 'value' keys."
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
            # Handle image deletions first
            images_to_delete = validated_data.pop('images_to_delete', [])
            if images_to_delete:
                ProductImage.objects.filter(
                    product=instance,
                    id__in=images_to_delete
                ).delete()

            # Handle primary image update
            primary_image_id = validated_data.pop('primary_image_id', None)
            if primary_image_id:
                # Reset all images to non-primary
                instance.images.all().update(is_primary=False)
                # Set the new primary image
                try:
                    primary_image = instance.images.get(id=primary_image_id)
                    primary_image.is_primary = True
                    primary_image.save()
                except ProductImage.DoesNotExist:
                    raise serializers.ValidationError({
                        "primary_image_id": "Image with this ID does not exist"
                    })

            # Handle new uploaded images
            uploaded_images = validated_data.pop('uploaded_images', [])
            if uploaded_images:
                # Check if there's any primary image
                has_primary = instance.images.filter(is_primary=True).exists()
                
                new_images = []
                for i, image in enumerate(uploaded_images):
                    # Make the first uploaded image primary only if no primary exists
                    is_primary = not has_primary and i == 0
                    new_images.append(
                        ProductImage(
                            product=instance,
                            image=image,
                            is_primary=is_primary
                        )
                    )
                
                if new_images:
                    ProductImage.objects.bulk_create(new_images)

            # Continue with the rest of the update logic
            features_data = validated_data.pop('features', [])
            category = validated_data.pop('category', None)
            
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
                instance.features.clear()
                feature_values = []
                for feature_data in features_data:
                    feature_name = feature_data.get('feature')
                    feature_value_text = feature_data.get('value')

                    feature, _ = Feature.objects.get_or_create(name=feature_name)
                    feature_value, _ = FeatureValue.objects.get_or_create(
                        feature=feature,
                        value=feature_value_text
                    )
                    feature_values.append(feature_value)

                instance.features.add(*feature_values)

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
    


        


    