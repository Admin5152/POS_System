from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

@login_required
def inventory_list_production(request):
    """Production-safe inventory list view"""
    try:
        from products.models import Product
        from .models import InventoryLog
        
        search_query = request.GET.get('search', '')
        low_stock = request.GET.get('low_stock', '')
        
        products = Product.objects.all()
        
        if search_query:
            products = products.filter(
                Q(product_name__icontains=search_query) |
                Q(barcode__icontains=search_query)
            )
        
        if low_stock:
            products = products.filter(stock_quantity__lte=10)
        
        # Pagination
        paginator = Paginator(products, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Get recent inventory logs
        recent_logs = InventoryLog.objects.all()[:10]
        
        context = {
            'page_obj': page_obj,
            'recent_logs': recent_logs,
            'search_query': search_query,
            'show_low_stock': bool(low_stock),
        }
        
        return render(request, 'inventory/inventory_list.html', context)
        
    except Exception as e:
        logger.error(f"Inventory list error: {str(e)}")
        return render(request, 'inventory/inventory_list.html', {
            'page_obj': None,
            'recent_logs': [],
            'error': 'Unable to load inventory. Please try again.'
        })
