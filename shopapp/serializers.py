from rest_framework import serializers
from .models import Product, Order, User


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'pk',
            'name',
            'description',
            'price',
            'discount',
            'created_at',
            'archived',
            'preview',
        )


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = (
#             'pk',
#             'password',
#             'last_login',
#             'is_superuser',
#             'username',
#             'last_name',
#             'email',
#             'is_staff',
#             'is_active',
#             'date_joined',
#             'first_name',
#         )


class OrderSerializer(serializers.ModelSerializer):
    products = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), many=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Order
        fields = (
            'pk',
            'delivery_address',
            'promocode',
            'created_at',
            'user',
            'receipt',
            'products'
        )


# class ModelASerializer(serializers.ModelSerializer):
#     related_models = serializers.PrimaryKeyRelatedField(queryset=ModelB.objects.all(), many=True)
#
#     class Meta:
#         model = ModelA
#         fields = ['id', 'name', 'related_models']