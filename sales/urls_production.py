from django.urls import path
from . import views_production

app_name = 'sales'

urlpatterns = [
    path('pos/', views_production.pos_view_production, name='pos'),
    path('api/product-search/', views_production.product_search_api_production, name='product_search_api'),
    path('checkout/', views_production.checkout_production, name='checkout'),
    path('receipts/', views_production.receipts_list, name='receipts_list'),
]
