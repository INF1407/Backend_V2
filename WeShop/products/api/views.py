from .serializer import CategorySerializer, ProductSerializer
from products.models import Product, Category

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class CategoryAPI(APIView):
    
    @swagger_auto_schema(
        operation_summary="Retrieve all categories",
        operation_description="Fetches and returns a list of all categories.",
        responses={
            200: openapi.Response(
                description="List of categories",
                schema=CategorySerializer(many=True)
            )
        }
    )
    def get(self, request):
        queryset =  Category.objects.all()
        serializer = CategorySerializer(queryset, many=True)
        return Response(serializer.data)

class ProductsAPI(APIView):
    
    @api_view(('GET',))
    @swagger_auto_schema(
        operation_summary="Retrieve a list of products",
        operation_description="Fetches and returns a list of available products. Optionally filters by category if a category_slug is provided.",
        manual_parameters=[
            openapi.Parameter(
                'category_slug',
                openapi.IN_QUERY,
                description="Slug of the category to filter products",
                type=openapi.TYPE_STRING,
                required=False
            )
        ],
        responses={
            200: openapi.Response(
                description="List of products",
                schema=ProductSerializer(many=True)
            ),
            404: openapi.Response(description="Category not found")
        }
    )
    def get_products_list(self, request, category_slug=None):
        
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            products = products.filter(category=category)
        else:
            products = Product.objects.filter(available=True)
        
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    
    @api_view(('GET',))
    @swagger_auto_schema(
        operation_summary="Retrieve product details",
        operation_description="Fetches and returns the details of a specific product by its ID and slug.",
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_PATH,
                description="ID of the product",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
            openapi.Parameter(
                'slug',
                openapi.IN_PATH,
                description="Slug of the product",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Product details",
                schema=ProductSerializer()
            ),
            404: openapi.Response(description="Product not found")
        }
    )
    def get_product_detail(self, request, id, slug):
        product = get_object_or_404(Product, id=id, slug=slug, available=True)
        serializer = ProductSerializer(data=product)
        
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_summary="Create a new product",
        operation_description="Allows an authenticated user to create a new product. The product will be associated with the authenticated user.",
        request_body=ProductSerializer,
        responses={
            201: openapi.Response(
                description="Product created successfully",
                schema=ProductSerializer()
            ),
            400: openapi.Response(
                description="Invalid data provided"
            ),
            401: openapi.Response(
                description="Invalid or missing token"
            )
        }
    )
    def post(self, request):
        try:
            # Extract the token from the Authorization header
            token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
        except (Token.DoesNotExist, IndexError):
            return Response({'error': 'Invalid or missing token.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Parse and validate product data
        data = request.data.copy()
        data['user'] = user.id  # Associate the product with the authenticated user
        serializer = ProductSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_summary="Update a product",
        operation_description="Allows the owner of a product to update its details. The user must be authenticated and the product must belong to them.",
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_PATH,
                description="ID of the product",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
            openapi.Parameter(
                'slug',
                openapi.IN_PATH,
                description="Slug of the product",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        request_body=ProductSerializer,
        responses={
            200: openapi.Response(
                description="Product updated successfully",
                schema=ProductSerializer()
            ),
            400: openapi.Response(
                description="Invalid data provided"
            ),
            401: openapi.Response(
                description="Invalid or missing token"
            ),
            403: openapi.Response(
                description="User is not the owner of the product"
            ),
            404: openapi.Response(
                description="Product not found"
            )
        }
    )
    def put(self, request, id, slug):
        try:
            # Extract the token from the Authorization header
            token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
        except (Token.DoesNotExist, IndexError):
            return Response({'error': 'Invalid or missing token.'}, status=status.HTTP_401_UNAUTHORIZED)

        product = get_object_or_404(Product, id=id, slug=slug)
        if product.user == user:
            # Update the product information
            serializer = ProductSerializer(product, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'You must be the owner of the product to update it.'}, status=status.HTTP_403_FORBIDDEN)

    @swagger_auto_schema(
        operation_summary="Delete a product",
        operation_description="Allows the owner of a product to delete it. The user must be authenticated and the product must belong to them.",
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_PATH,
                description="ID of the product",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
            openapi.Parameter(
                'slug',
                openapi.IN_PATH,
                description="Slug of the product",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            204: openapi.Response(
                description="Product deleted successfully"
            ),
            401: openapi.Response(
                description="Invalid or missing token"
            ),
            403: openapi.Response(
                description="User is not the owner of the product"
            ),
            404: openapi.Response(
                description="Product not found"
            )
        }
    )
    def delete(self, request, id, slug):
        try:
            # Extract the token from the Authorization header
            token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
        except (Token.DoesNotExist, IndexError):
            return Response({'error': 'Invalid or missing token.'}, status=status.HTTP_401_UNAUTHORIZED)

        product = get_object_or_404(Product, id=id, slug=slug)
        if product.user == user:
            # Delete the product
            product.delete()
            return Response({'message': 'Product deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': 'You must be the owner of the product to delete it.'}, status=status.HTTP_403_FORBIDDEN)
