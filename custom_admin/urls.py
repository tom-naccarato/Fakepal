from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('all_users/', views.all_users, name='all_users'),
    path('all_transactions/', views.all_transactions, name='all_transactions'),
]
