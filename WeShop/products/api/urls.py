from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path("api/", 
        views.ProductAPI.as_view(),
        name = 'api-products'),
    path("list/",
         views.ProductsListAPI.as_view(),
         name = 'list-products'),
    path("categories/",
         views.CategoryListAPI.as_view(),
         name = 'categories'),
]