from django.urls import path
from . import views

app_name = 'account'

urlpatterns = [
    path("list/",
         views.ProfileView.as_view(),
         name = 'list-accounts'),
]