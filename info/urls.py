"""
URL configuration for info project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from info import views  # Import your views from the 'info' app
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),  # Root URL redirects to the home page
    path("admin/", admin.site.urls),
    path('api/info/', views.get_customer_info, name='customer_info'),  # Use the correct view function name
    path('api/predict_stock_api/', views.predict_stock_api, name='predict_stock_api'),  # Use the correct view function name
    path('sign-in/', views.sign_in, name='sign-in'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

