from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = User
        fields = ['id', 'username', 'password', 'email']

from .models import ProductModel, CartModel

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductModel
        fields = ['id', 'name', 'image_url', 'price', 'created_by', 'created_date', 'modified_date', 'star_review']

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartModel
        fields = "__all__"

class CartDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.StringRelatedField()
    image_url = serializers.StringRelatedField()
    price = serializers.IntegerField()
    total_order = serializers.IntegerField()

class ProductSearchSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.StringRelatedField()
    image_url = serializers.StringRelatedField()
    price = serializers.IntegerField()
    created_by = serializers.StringRelatedField()
    created_date = serializers.DateField()
    modified_date = serializers.DateField()
    star_review = serializers.IntegerField()

