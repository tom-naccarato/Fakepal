from django.urls import path
from . import views

urlpatterns = [
    path('transactions/', views.transactions, name='transactions'),
    path('admin_all_users/', views.admin_all_users, name='admin_all_users'),
    path('admin_all_transactions/', views.admin_all_transactions, name='admin_all_transactions'),
    path('requests/', views.requests, name='requests'),
    path('make_request/', views.make_request, name='make_request'),
    path('accept_request/<int:request_id>/', views.accept_request, name='accept_request'),
    path('decline_request/<int:request_id>/', views.decline_request, name='decline_request'),
    path('cancel_request/<int:request_id>/', views.cancel_request, name='cancel_request'),
    path('send_payment/', views.send_payment, name='send_payment'),
]
