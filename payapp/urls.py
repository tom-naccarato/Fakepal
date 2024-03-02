from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('transactions/', views.transactions, name='transactions'),
    path('admin_all_users/', views.admin_all_users, name='admin_all_users'),
]