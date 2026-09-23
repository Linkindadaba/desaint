from django.urls import path
from . import views

app_name = 'invoices'

urlpatterns = [
    path('<int:pk>/', views.invoice_proforma, name='proforma'),
    path('sample/', views.invoice_sample, name='sample'),
]
