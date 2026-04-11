from django.urls import path
from . import views_production

app_name = 'products'

urlpatterns = [
    path('list/', views_production.product_list_production, name='list'),
    path('<int:pk>/', views_production.product_detail_production, name='detail'),
]
