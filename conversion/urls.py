from django.urls import path
from .views import ConversionAPI

urlpatterns = [
    path('<str:from_currency>/<str:to_currency>/<str:amount>/', ConversionAPI.as_view(), name='conversion'),
]
