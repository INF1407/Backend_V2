from orders.models import Order, OrderItem
from cart.models import Cart
from products.models import Product

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class OrdersAPI(APIView):
    
    def put(self, request):
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