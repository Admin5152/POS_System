from django.contrib import admin
from .models import Category, Product

admin.site.register(Category)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'price', 'stock_quantity', 'barcode')
    search_fields = ('product_name', 'barcode')
    list_filter = ('category',)
