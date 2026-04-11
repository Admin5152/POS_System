from django.db import models
from sales.models import Sale

class Payment(models.Model):
    sale = models.ForeignKey(Sale, related_name='payments', on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_reference = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} for Sale #{self.sale.id} - {self.amount} ({self.status})"
