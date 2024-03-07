from . import views
from django.urls import path

urlpatterns = [
    path('conversion/', views.conversion, name='conversion'),
]