from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('paystack/start/', views.initialize_payment, name='paystack_start'),
    path('paystack/verify/<str:reference>/', views.verify_payment, name='paystack_verify'),
]
