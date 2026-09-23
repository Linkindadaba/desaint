from django.urls import path
from . import views

app_name = 'orders'

# Staff-only POS routes — mounted at /admin/pos/ in config/urls.py
urlpatterns = [
    path('', views.pos_terminal, name='pos_terminal'),
    path('submit/', views.pos_submit_sale, name='pos_submit_sale'),
    path('history/', views.pos_history, name='pos_history'),
    path('receipt/<int:pk>/', views.pos_receipt_detail, name='pos_receipt'),
]
