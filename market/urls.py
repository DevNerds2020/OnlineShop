from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('product/list/', views.get_products),
    path('product/<int:id>/', views.get_product),
    path('product/insert/', views.add_product),
    path('product/<int:id>/edit_inventory/', views.edit_inventory),
    path('shopping/cart/', views.watch_orders),
    path('shopping/cart/add_items/', views.add_items),
    path('shopping/cart/remove_items/', views.remove_items),
    path('shopping/submit/', views.submit)
]