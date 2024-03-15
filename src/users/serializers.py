from rest_framework import serializers
from .models import Cart,CartItem,Product


class AddtoCartSerializer(serializers.Serializer):
    product_uuid = serializers.UUIDField()


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "name",
            "image",
            "uuid",
            "price"
        ]


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = CartItem
        fields = [
            "quantity",
            "product"
        ]

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)
    class Meta:
        model = Cart
        fields = [
            "items"
        ]