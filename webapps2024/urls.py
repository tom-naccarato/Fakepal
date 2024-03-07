"""
URL configuration for webapps2024 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
import payapp.views


urlpatterns = [
    path('webapps2024/', include([
        path('home/', payapp.views.home, name='home'),
        path('register/', include(('register.urls', 'register'), namespace='register')),
        path('', include(('payapp.urls', 'payapp'), namespace='payapp')),
        path('admin/', include(('custom_admin.urls', 'custom_admin'), namespace='admin')),
        path('conversion/', include(('conversion.urls', 'conversion'), namespace='conversion')),
    ]))
]
