from rest_framework import serializers
from orders.models import Order, OrderItem
from products.models import Product
from django.contrib.auth.models import User

class OrderSerializer(serializers.ModelSerializer):
    
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    class Meta:
        model = Order
        fields = [
            'id', 'first_name', 'last_name', 'email',
            'user', 'address', 'postal_code', 'city',
            'created', 'updated', 'paid',
        ]
        
class OrderItemsSerializer(serializers.ModelSerializer):

    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    
    class Meta:
        model = OrderItem
        fields = ['order', 'product', 'price', 'quantity']