from rest_framework import serializers
from products.models import Category, Product
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class ProductSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())  # Accept category ID for write operations
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'image', 'description', 'price', 
            'available', 'created', 'updated', 'category', 'user'
        ]
