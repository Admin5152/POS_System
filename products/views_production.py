from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

@login_required
def product_list_production(request):
    """Production-safe product list view"""
    try:
        from .models import Product, Category
        
        search_query = request.GET.get('search', '')
        category_id = request.GET.get('category', '')
        
        products = Product.objects.all()
        
        if search_query:
            products = products.filter(
                Q(product_name__icontains=search_query) |
                Q(barcode__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        if category_id:
            products = products.filter(category_id=category_id)
        
        categories = Category.objects.all()
        
        # Pagination
        paginator = Paginator(products, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'categories': categories,
            'search_query': search_query,
            'selected_category': category_id,
        }
        
        return render(request, 'products/product_list.html', context)
        
    except Exception as e:
        logger.error(f"Product list error: {str(e)}")
        return render(request, 'products/product_list.html', {
            'page_obj': None,
            'categories': [],
            'error': 'Unable to load products. Please try again.'
        })

@login_required
def product_detail_production(request, pk):
    """Production-safe product detail view"""
    try:
        from .models import Product
        product = get_object_or_404(Product, pk=pk)
        return render(request, 'products/product_detail.html', {'product': product})
    except Exception as e:
        logger.error(f"Product detail error: {str(e)}")
        return render(request, 'products/product_detail.html', {'error': 'Product not found.'})
