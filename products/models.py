from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Product(models.Model):
    product_name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Cost of goods sold for profit calculation")
    stock_quantity = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=10, help_text="Minimum stock level before reordering is required")
    barcode = models.CharField(max_length=100, unique=True, null=True, blank=True)
    supplier = models.CharField(max_length=200, null=True, blank=True)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)

    def __str__(self):
        return self.product_name
    
    @property
    def profit_margin(self):
        if self.price > 0:
            return ((self.price - self.cost_price) / self.price) * 100
        return 0
