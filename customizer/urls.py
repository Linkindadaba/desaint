from django.urls import path
from . import views

app_name = 'customizer'

urlpatterns = [
    path('', views.configurator, name='configurator'),
    path('submit/', views.customizer_submit, name='submit'),
    path('proof/<int:pk>/', views.proof_detail, name='proof_detail'),
    path('proof/sample/', views.proof_approval, name='proof_sample'),
]

