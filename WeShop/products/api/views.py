from .serializer import CategorySerializer, ProductSerializer
from products.models import Product, Category

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.parsers import JSONParser

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class CategoryListAPI(APIView):
    
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

class ProductsListAPI(APIView):

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
    def get(self, request):
        category_slug = request.query_params.get('category_slug', None)
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            products = Product.objects.filter(category=category, available=True)
        else:
            products = Product.objects.filter(available=True)

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProductAPI(APIView):
    
    @swagger_auto_schema(
    operation_summary="Retrieve product details",
    operation_description="Fetches and returns the details of a specific product based on its ID and slug provided in the request body.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["id", "slug"],
        properties={
            "id": openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description="ID of the product"
            ),
            "slug": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Slug of the product"
            )
        }
    ),
    responses={
        200: openapi.Response(
            description="Product details retrieved successfully",
            schema=ProductSerializer()
        ),
        400: openapi.Response(
            description="Missing or invalid fields in request body",
            examples={
                "application/json": {
                    "error": 'Both "id" and "slug" are required in the request body.'
                }
            }
        ),
        404: openapi.Response(description="Product not found"),
        500: openapi.Response(description="Unexpected server error")
    }
)
    def get(self, request):
        try:
            
            data = request.data
            product_id = data.get('id')
            product_slug = data.get('slug')

            if not product_id or not product_slug:
                
                return Response(
                    {'error': 'Both "id" and "slug" are required in the request body.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Fetch the product based on id and slug
            product = get_object_or_404(Product, id=product_id, slug=product_slug, available=True)
            
            # Serialize the product
            serializer = ProductSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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
    operation_description="Allows the owner of a product to update its details. The `id` and `slug` of the product must be provided in the request body.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["id", "slug"],  # This indicates required fields
        properties={
            "id": openapi.Schema(
                type=openapi.TYPE_INTEGER,
                description="ID of the product"
            ),
            "slug": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Slug of the product"
            ),
            "name": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Updated name of the product"
            ),
            "description": openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Updated description of the product"
            ),
            "price": openapi.Schema(
                type=openapi.TYPE_NUMBER,
                format=openapi.FORMAT_FLOAT,
                description="Updated price of the product"
            ),
            "available": openapi.Schema(
                type=openapi.TYPE_BOOLEAN,
                description="Whether the product is available"
            )
        }
    ),
    responses={
        200: openapi.Response(
            description="Product updated successfully",
            schema=ProductSerializer()
        ),
        400: openapi.Response(
            description="Invalid data provided",
            examples={
                "application/json": {
                    "error": 'Both "id" and "slug" are required in the request body.'
                }
            }
        ),
        401: openapi.Response(description="Invalid or missing token"),
        403: openapi.Response(description="User is not the owner of the product"),
        404: openapi.Response(description="Product not found"),
        500: openapi.Response(description="Unexpected server error")
    }
)
    def put(self, request):
        try:
            # Extract the token from the Authorization header
            token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
        except (Token.DoesNotExist, IndexError):
            return Response({'error': 'Invalid or missing token.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            
            data = request.data
            product_id = data.get('id')
            product_slug = data.get('slug')

            if not product_id or not product_slug:
                return Response(
                    {'error': 'Both "id" and "slug" are required in the request body.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Fetch the product based on id and slug
            product = get_object_or_404(Product, id=product_id, slug=product_slug)

            # Check if the user is the owner of the product
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
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_summary="Delete a product",
        operation_description="Allows the owner of a product to delete it. The `id` and `slug` of the product must be provided in the request body.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["id", "slug"],
            properties={
                "id": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID of the product"
                ),
                "slug": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Slug of the product"
                )
            }
        ),
        responses={
            204: openapi.Response(
                description="Product deleted successfully"
            ),
            401: openapi.Response(description="Invalid or missing token"),
            403: openapi.Response(description="User is not the owner of the product"),
            404: openapi.Response(description="Product not found"),
            500: openapi.Response(description="Unexpected server error")
        }
    )
    def delete(self, request):
        try:
            # Extract the token from the Authorization header
            token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
        except (Token.DoesNotExist, IndexError):
            return Response({'error': 'Invalid or missing token.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            data = request.data
            product_id = data.get('id')
            product_slug = data.get('slug')
            product = get_object_or_404(Product, id=product_id , slug=product_slug)
            if product.user == user:
                # Delete the product
                product.delete()
                return Response({'message': 'Product deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'error': 'You must be the owner of the product to delete it.'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)