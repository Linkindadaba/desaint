from django.urls import path
from . import views

app_name = 'customizer'

urlpatterns = [
    path('', views.configurator, name='configurator'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:pk>/status/', views.order_status_update, name='order_status_update'),
    path('orders/<int:pk>/delete/', views.order_delete, name='order_delete'),
    path('submit/', views.customizer_submit, name='submit'),
    path('proof/<int:pk>/', views.proof_detail, name='proof_detail'),
    path('proof/sample/', views.proof_approval, name='proof_sample'),
]
