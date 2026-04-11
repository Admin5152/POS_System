from django.urls import path
from . import views_production

app_name = 'inventory'

urlpatterns = [
    path('list/', views_production.inventory_list_production, name='list'),
]
