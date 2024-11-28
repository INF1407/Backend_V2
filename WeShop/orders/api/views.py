from orders.models import Order, OrderItem
from cart.models import Cart
from products.models import Product
from .serializer import OrderSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class OrdersAPI(APIView):
    
    @swagger_auto_schema(
    operation_summary="Create an order from the user's cart",
    operation_description="Allows an authenticated user to create an order using their current cart. Order details and cart items are processed, and the cart is cleared after the order is created.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "order_data": openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=["first_name", "last_name", "email", "address", "postal_code", "city"],
                properties={
                    "first_name": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="First name of the user"
                    ),
                    "last_name": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Last name of the user"
                    ),
                    "email": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        format=openapi.FORMAT_EMAIL,
                        description="Email address of the user"
                    ),
                    "address": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Shipping address"
                    ),
                    "postal_code": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Postal code"
                    ),
                    "city": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="City for delivery"
                    )
                },
                description="Details required for placing an order"
            )
        },
        required=["order_data"]
    ),
    responses={
        201: openapi.Response(
            description="Order created successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "order_id": openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        description="Unique ID of the created order"
                    ),
                    "total_cost": openapi.Schema(
                        type=openapi.TYPE_NUMBER,
                        format=openapi.FORMAT_FLOAT,
                        description="Total cost of the order"
                    ),
                    "created_at": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        format=openapi.FORMAT_DATETIME,
                        description="Timestamp when the order was created"
                    ),
                    "updated_at": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        format=openapi.FORMAT_DATETIME,
                        description="Timestamp when the order was last updated"
                    ),
                    "items": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "product_id": openapi.Schema(
                                    type=openapi.TYPE_INTEGER,
                                    description="ID of the product"
                                ),
                                "product_name": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    description="Name of the product"
                                ),
                                "price": openapi.Schema(
                                    type=openapi.TYPE_NUMBER,
                                    format=openapi.FORMAT_FLOAT,
                                    description="Price of the product"
                                ),
                                "quantity": openapi.Schema(
                                    type=openapi.TYPE_INTEGER,
                                    description="Quantity of the product"
                                )
                            }
                        ),
                        description="List of items in the order"
                    )
                }
            )
        ),
        400: openapi.Response(
            description="Invalid order_data format",
            examples={
                "application/json": {
                    "error": "Invalid order_data format. Expected a dictionary."
                }
            }
        ),
        401: openapi.Response(description="Invalid or missing token"),
        404: openapi.Response(
            description="Cart or product not found",
            examples={
                "application/json": {
                    "error": "Cart not found for the user."
                }
            }
        ),
        500: openapi.Response(description="Unexpected server error")
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

        try:
            # Extract order data from the request
            order_data = request.data.get('order_data')
            if not isinstance(order_data, dict):
                return Response({'error': 'Invalid order_data format. Expected a dictionary.'}, status=status.HTTP_400_BAD_REQUEST)

            # Create the Order
            order = Order.objects.create(
                user=user,
                first_name=order_data.get('first_name'),
                last_name=order_data.get('last_name'),
                email=order_data.get('email'),
                address=order_data.get('address'),
                postal_code=order_data.get("postal_code"),
                city=order_data.get("city"),
            )
            
            # Fetch the user's cart
            cart = Cart.objects.get(user=user)
            cart_items = cart.items

            # Add items from the cart to the Order
            for product_id, quantity in cart_items.items():
                product = Product.objects.get(id=product_id)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=product.price,
                    quantity=quantity
                )

            # Clear the cart after creating the Order
            cart.clear_cart()

            # Prepare the response data
            response_data = {
                "order_id": order.id,
                "total_cost": order.get_total_cost(),
                "created_at": order.created,
                "updated_at": order.updated,
                "items": [
                    {
                        "product_id": item.product.id,
                        "product_name": item.product.name,
                        "price": item.price,
                        "quantity": item.quantity
                    }
                    for item in order.items.all()
                ]
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Cart.DoesNotExist:
            return Response({'error': 'Cart not found for the user.'}, status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            return Response({'error': 'One or more products in the cart do not exist.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def get(self, request):
        
        try:
            # Extract the token from the Authorization header
            token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]
            token_obj = Token.objects.get(key=token)
            user = token_obj.user
        except (Token.DoesNotExist, IndexError):
            return Response({'error': 'Invalid or missing token.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        orders = Order.objects.filter(user = user)
        response_data = {}
        for order in orders:
            response_data[order.id] = [
                {
                "total_cost": order.get_total_cost(),
                "address": order.address,
                "postal_code": order.postal_code,
                "city": order.city,
                "paid": order.paid,
                "created_at": order.created,
                "updated_at": order.updated,
                "items": [
                    {
                        "product_id": item.product.id,
                        "product_name": item.product.name,
                        "price": item.price,
                        "quantity": item.quantity
                    }
                    for item in order.items.all()
                ]
                }
                ]
        return Response(response_data, status=status.HTTP_200_OK)
            
        
        