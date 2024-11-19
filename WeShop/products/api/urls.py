from django.urls import path, include
from . import views

app_name = 'products'

urlpatterns = [
    path("merchandize/", 
        views.ProductsAPI.as_view(),
        name = 'merchandize'),
    path("categories/",
         views.CategoryAPI.as_view(),
         name = 'categories'),
]