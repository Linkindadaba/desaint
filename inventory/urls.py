from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('ledger/', views.stock_ledger, name='ledger'),
    path('movements/', views.movements_log, name='movements'),
    path('suppliers/', views.suppliers_view, name='suppliers'),
    path('supplier/<int:pk>/edit/', views.edit_supplier, name='edit_supplier'),
    path('supplier/<int:pk>/delete/', views.delete_supplier, name='delete_supplier'),
    path('item/<int:pk>/restock/', views.restock_item, name='restock'),
    path('item/<int:pk>/unbox/', views.break_bulk_unbox, name='unbox'),
    path('item/<int:pk>/adjust/', views.adjust_stock, name='adjust'),
    path('item/<int:pk>/config/', views.edit_item_config, name='edit_config'),
]
