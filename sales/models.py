from django.db import models
from django.conf import settings
from customers.models import Customer
from products.models import Product

class Sale(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    PAYMENT_CHOICES = (
        ('cash', 'Cash'),
        ('momo', 'Mobile Money'),
        ('card', 'Debit/Credit Card'),
    )
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash')

    def __str__(self):
        return f"Sale #{self.id} - {self.date.strftime('%Y-%m-%d %H:%M')}"

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2) # price at the time of sale

    def __str__(self):
        return f"{self.quantity} x {self.product.product_name if self.product else 'Unknown Product'} (Sale #{self.sale.id})"

class Return(models.Model):
    sale_item = models.ForeignKey(SaleItem, on_delete=models.CASCADE, related_name='returns')
    date_returned = models.DateTimeField(auto_now_add=True)
    reason = models.TextField()
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"Return for {self.sale_item.product.product_name if self.sale_item.product else 'Unknown'} (Sale #{self.sale_item.sale.id})"
