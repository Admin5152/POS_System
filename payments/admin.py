from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('sale', 'payment_method', 'amount', 'status', 'transaction_reference', 'created_at')
    list_filter = ('payment_method', 'status')
