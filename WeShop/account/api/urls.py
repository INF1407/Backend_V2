from django.urls import path, include
from . import views

app_name = 'account'

urlpatterns = [
    
    path("profile/",
         views.UserAPI.as_view(),
         name = 'register-account'),
     path('token-auth/', 
          views.CustomAuthToken.as_view(), 
          name='token-auth'),
     path('password_reset/',
          include('django_rest_passwordreset.urls',
          namespace='password_reset')),
]