from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    path('', views.customer_list, name='list'),
    path('add/', views.add_customer, name='add'),
    path('edit/<int:pk>/', views.edit_customer, name='edit'),
]
