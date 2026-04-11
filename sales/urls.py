from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('pos/', views.pos_view, name='pos'),
    path('checkout/', views.checkout, name='checkout'),
    path('receipt/<int:sale_id>/', views.receipt_view, name='receipt'),
    path('receipts/', views.receipts_list, name='receipts'),
    path('api/product-search/', views.product_search_api, name='api_product_search'),
    path('returns/', views.process_return, name='returns'),
]
