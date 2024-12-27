from rest_framework import serializers

class UserSerializer(serializers.Serializer):
    age = serializers.IntegerField()
    category_1 = serializers.CharField()
    category_2 = serializers.CharField()
    category_3 = serializers.CharField()
    gender = serializers.CharField()
    psychological_traits = serializers.CharField()
    favorite_material = serializers.CharField()
    favorite_design = serializers.CharField()
    occasions = serializers.CharField()
    relationship = serializers.CharField()


class ResultSerializer(serializers.Serializer):
    product_id = serializers.ListField(
        child = serializers.FloatField(),
        required = True
    )