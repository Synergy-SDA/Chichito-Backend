from rest_framework import serializers
from .models import *


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
    

# class ProductSerializer(serializers.ModelSerializer):
#     category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all()) 
#     product_features = ProductFeatureSerializer(many=True)  # This will handle the list of features

#     class Meta:
#         model = Product
#         fields = ['name', 'description', 'price', 'count_exist', 'is_available', 'category', 'product_features']

#     def validate_price(self, value):
#         if value < 0:
#             raise serializers.ValidationError("قیمت منفی نمی‌تواند باشد.")
#         return value

#     def validate_count_exist(self, value):
#         if value < 0:
#             raise serializers.ValidationError("تعداد موجودی منفی نمی‌تواند باشد.")
#         return value

#     def create(self, validated_data):
#         # Remove category and product_features from the validated data to handle them separately
#         category_data = validated_data.pop('category')
#         product_features_data = validated_data.pop('product_features')

#         # Create the product first
#         product = Product.objects.create(**validated_data)

#         # Attach the category to the product after creation
#         product.category = Category.objects.get(id=category_data)
#         product.save()
#         print(product)

#         # Now that the product is created, handle the product_features
#         for feature_data in product_features_data:
#             feature_value_data = feature_data.pop('feature_value')  # Get the feature_value data
            
#             # Get or create the feature_value based on feature name and value
#             feature = feature_value_data['feature']
#             value = feature_value_data['value']
#             feature_value, created = FeatureValue.objects.get_or_create(feature=feature, value=value)

#             # Create ProductFeature relation between the product and feature_value
#             ProductFeature.objects.create(
#                 product=product,  # Now the product is available
#                 feature_value=feature_value
#             )

#         return product

