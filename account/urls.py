from django.urls import path
from . import views

urlpatterns = [
    path('accounts', views.list_account),
    path('accounts/<str:pk>/', views.account_detail),
]