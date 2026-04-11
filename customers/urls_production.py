from django.urls import path
from . import views_production

app_name = 'customers'

urlpatterns = [
    path('list/', views_production.customer_list_production, name='list'),
    path('<int:pk>/', views_production.customer_detail_production, name='detail'),
]
