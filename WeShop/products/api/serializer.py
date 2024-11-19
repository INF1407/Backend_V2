from rest_framework import serializers
from products.models import Category, Product

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class ProductSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Display the username of the product owner
    category = serializers.StringRelatedField()  # Display the category name instead of ID

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'image', 'description', 'price', 
            'available', 'created', 'updated', 'category', 'user'
        ]
