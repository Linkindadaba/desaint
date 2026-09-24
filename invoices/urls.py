from django.urls import path
from . import views

app_name = 'invoices'

urlpatterns = [
    path('', views.invoice_list, name='invoice_list'),
    path('create/', views.invoice_create, name='invoice_create'),
    path('<int:pk>/', views.invoice_proforma, name='proforma'),
    path('<int:pk>/mark-paid/', views.invoice_mark_paid, name='mark_paid'),
    path('<int:pk>/delete/', views.invoice_delete, name='delete'),
    path('sample/', views.invoice_sample, name='sample'),
]
