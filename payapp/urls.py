from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('transactions/', views.transactions, name='transactions'),
    path('admin_all_users/', views.admin_all_users, name='admin_all_users'),
    path('admin_all_transactions/', views.admin_all_transactions, name='admin_all_transactions'),
    path('requests/', views.requests, name='requests'),
    path('make_request/', views.make_request, name='make_request'),
    path('accept_request/<int:request_id>/', views.accept_request, name='accept_request'),
]
