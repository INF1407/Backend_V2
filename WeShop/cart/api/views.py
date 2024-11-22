from cart.models import Cart

from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class CartAPI(APIView):

    @swagger_auto_schema(
        operation_summary="Retrieve the user's cart",
        operation_description="Fetches and returns the cart for the authenticated user. Requires a valid authentication token.",
        responses={
            200: openapi.Response(
                description="Cart retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "user": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Username of the cart owner"
                        ),
                        "items": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            additional_properties=openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description="Quantity of the product"
                            ),
                            description="A dictionary of product IDs and their quantities"
                        ),
                        "created_at": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            format=openapi.FORMAT_DATETIME,
                            description="Timestamp when the cart was created"
                        ),
                        "updated_at": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            format=openapi.FORMAT_DATETIME,
                            description="Timestamp when the cart was last updated"
                        )
                    }
                )
            ),
            401: openapi.Response(description="Invalid or missing token"),
            404: openapi.Response(description="Cart not found")
        }
    )
    def get(self, request):
        try:
            # Extract the token from the Authorization header
            token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
        except (Token.DoesNotExist, IndexError):
            return Response({'error': 'Invalid or missing token.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Fetch or create a cart for the user
        cart, created = Cart.objects.get_or_create(user=user)
        if created:
            cart.save()  # Save the newly created cart

        # Prepare the cart data for response
        cart_data = {
            "user": user.username,
            "items": cart.items,  # The dictionary of product IDs and quantities
            "created_at": cart.created_at,
            "updated_at": cart.updated_at
        }

        return Response(cart_data, status=status.HTTP_200_OK)
    

    @swagger_auto_schema(
        operation_summary="Update the user's cart",
        operation_description="Allows the authenticated user to update their cart with new items. The `items` field must be a dictionary containing product IDs as keys and quantities as values.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "items": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    additional_properties=openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        description="Quantity of the product"
                    ),
                    description="A dictionary of product IDs and their quantities"
                )
            },
            required=["items"]
        ),
        responses={
            200: openapi.Response(
                description="Cart updated successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "user": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Username of the cart owner"
                        ),
                        "items": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            additional_properties=openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description="Quantity of the product"
                            ),
                            description="Updated cart items"
                        ),
                        "created_at": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            format=openapi.FORMAT_DATETIME,
                            description="Timestamp when the cart was created"
                        ),
                        "updated_at": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            format=openapi.FORMAT_DATETIME,
                            description="Timestamp when the cart was last updated"
                        )
                    }
                )
            ),
            400: openapi.Response(
                description="Invalid items format",
                examples={
                    "application/json": {
                        "error": "Invalid items format. Expected a dictionary of product IDs and quantities."
                    }
                }
            ),
            401: openapi.Response(description="Invalid or missing token"),
            404: openapi.Response(description="Cart not found"),
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

        # Fetch or create a cart for the user
        cart = get_object_or_404(Cart, user=user)

        try:
            # Extract items from the request body
            items = request.data.get('items')
            if not isinstance(items, dict):
                return Response({'error': 'Invalid items format. Expected a dictionary of product IDs and quantities.'}, status=status.HTTP_400_BAD_REQUEST)

            # Update the cart's items
            cart.items = items
            cart.save()

            # Prepare the response data
            cart_data = {
                "user": user.username,
                "items": cart.items,  # Updated items dictionary
                "created_at": cart.created_at,
                "updated_at": cart.updated_at
            }

            return Response(cart_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
