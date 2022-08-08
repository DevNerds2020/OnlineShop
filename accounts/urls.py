from django.urls import path
from . import views

urlpatterns = [
    path('customer/register/', views.register_customer),
    path('customer/list/', views.customer_list),
    path('customer/<int:id>/', views.customer_data),
    path('customer/<int:id>/edit/', views.customer_edit),
    path('customer/login/', views.customer_login),
    path('customer/logout/', views.customer_logout),
    path('customer/profile/', views.customer_profile),
]
