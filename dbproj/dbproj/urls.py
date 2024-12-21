"""
URL configuration for dbproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from laba6.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('all-records/', all_records_view, name='all_records'),
    path('upload-sql/', upload_sql_file_view, name='upload_sql'),  # Додаємо новий маршрут
    path('', home_view, name='home'),
    path('all-products/', all_products_view, name='all_products'),
    path('place-order/', place_order, name='place_order'),
    path('confirm-order/<int:article>/', confirm_order, name='confirm_order'),
    path('order-confirmation/<int:order_id>/', order_confirmation, name='order_confirmation'),
    path('suppliers/', list_and_delete_suppliers, name='list_and_delete_suppliers'),
    path('update-client/', update_client, name='update_client'),
    path('perform-update-client/', perform_update_client, name='perform_update_client'),
    path('load-records-dif/load-records/', load_records_view, name='load_records'),
    path('load-records-dif/', load_records_dif, name='load_records_dif'),
    path('api/get-clients', get_clients, name="get_clients"),
    path('api/get-products', get_products, name="get_products"),
    path('api/get-orders', get_orders, name="get_orders"),
]

# get_products
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)