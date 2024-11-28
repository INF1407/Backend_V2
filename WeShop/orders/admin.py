from django.contrib import admin

from .models import Order, OrderItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'email', 'address',
                     ]
    list_filter = ['user', 'created', 'updated']
    

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'price',
                     ]
    list_filter = ['order',]
    list_editable = ['price']
    
