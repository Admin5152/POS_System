from django.contrib import admin
from .models import InventoryLog

@admin.register(InventoryLog)
class InventoryLogAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'quantity_changed', 'reason', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('product__product_name',)
