from django.db import models
from django.conf import settings
from products.models import Product
from django.core.serializers.json import DjangoJSONEncoder

class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart"
    )
    items = models.JSONField(
        default=dict,  # The dictionary will store product IDs as keys and quantities as values
        encoder=DjangoJSONEncoder
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    def add_product(self, product, quantity=1):
        """
        Add a product to the cart or update its quantity if already in the cart.
        """
        if str(product.id) in self.items:
            self.items[str(product.id)] += quantity
        else:
            self.items[str(product.id)] = quantity
        self.save()

    def remove_product(self, product):
        """
        Remove a product from the cart.
        """
        product_id = str(product.id)
        if product_id in self.items:
            del self.items[product_id]
            self.save()

    def clear_cart(self):
        """
        Clear all items in the cart.
        """
        self.items = {}
        self.save()

    def get_total_items(self):
        """
        Get the total number of items in the cart.
        """
        return sum(self.items.values())

    def get_total_price(self):
        """
        Calculate the total price of the cart.
        """
        total = 0
        for product_id, quantity in self.items.items():
            product = Product.objects.get(id=product_id)
            total += product.price * quantity
        return total
