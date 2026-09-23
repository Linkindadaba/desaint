from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('citations/', views.citations, name='citations'),
    path('contact/', views.contact, name='contact'),
]
