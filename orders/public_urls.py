"""
orders/public_urls.py — Public-facing cart & checkout routes for B2C customers.
These routes live at /orders/ and are NOT behind any auth guard.
"""
from django.urls import path
from . import views

app_name = 'orders_public'

urlpatterns = [
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.checkout, name='checkout'),
    path('confirmation/<int:pk>/', views.order_confirmation, name='order_confirmation'),
]
