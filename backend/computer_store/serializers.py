from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ProductModel, CartModel, PurchasingModel, PurchasingDetailModel

class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = User
        fields = ['id', 'username', 'email']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductModel
        fields = ['id', 'name', 'image_url', 'price', 'created_by', 'created_date', 'modified_date', 'star_review']

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartModel
        fields = "__all__"

class CartDetailSerializer(serializers.Serializer):
    id_product = serializers.StringRelatedField()
    name = serializers.StringRelatedField()
    image_url = serializers.SerializerMethodField()
    price = serializers.IntegerField()
    total_order = serializers.IntegerField()
    id_cart = serializers.StringRelatedField()

    def get_image_url(self, obj):
        storage_location = '/media'
        return f'{storage_location}/{obj["image_url"]}'

class ProductSearchSerializer(serializers.Serializer):
    id = serializers.StringRelatedField()
    name = serializers.StringRelatedField()
    image_url = serializers.SerializerMethodField()
    price = serializers.IntegerField()
    created_by = serializers.StringRelatedField()
    created_date = serializers.DateField()
    modified_date = serializers.DateField()
    star_review = serializers.IntegerField()

    def get_image_url(self, obj):
        storage_location = '/media'
        return f'{storage_location}/{obj["image_url"]}'
    
class PurchasingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchasingModel
        fields = "__all__"

class PurchasingDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchasingDetailModel
        fields = "__all__"

class PurchasedSerializer(serializers.Serializer):
    name = serializers.StringRelatedField()
    image_url = serializers.SerializerMethodField()
    price = serializers.IntegerField()
    created_date = serializers.DateField()
    total_price = serializers.IntegerField()
    total_unit = serializers.IntegerField()

    def get_image_url(self, obj):
        storage_location = '/media'
        return f'{storage_location}/{obj["image_url"]}'
