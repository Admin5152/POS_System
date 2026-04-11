from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.inventory_list, name='list'),
    path('adjust/<int:product_id>/', views.adjust_stock, name='adjust'),
]
