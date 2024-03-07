from . import views
from django.urls import path

urlpatterns = [
    path('<str:currency1>/<str:currency2>/<str:amount_of_currency1>', views.conversion, name='conversion'),
]