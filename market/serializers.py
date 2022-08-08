from market.models import *
from rest_framework import serializers


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'code', 'name', 'price', 'inventory']


class OrderRowSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderRow
        fields = ['product', 'order', 'amount']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['customer', 'order_time', 'total_price', 'status']
