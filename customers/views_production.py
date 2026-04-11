from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

@login_required
def customer_list_production(request):
    """Production-safe customer list view"""
    try:
        from .models import Customer
        
        search_query = request.GET.get('search', '')
        
        customers = Customer.objects.all()
        
        if search_query:
            customers = customers.filter(
                Q(name__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        
        # Pagination
        paginator = Paginator(customers, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'search_query': search_query,
        }
        
        return render(request, 'customers/customer_list.html', context)
        
    except Exception as e:
        logger.error(f"Customer list error: {str(e)}")
        return render(request, 'customers/customer_list.html', {
            'page_obj': None,
            'error': 'Unable to load customers. Please try again.'
        })

@login_required
def customer_detail_production(request, pk):
    """Production-safe customer detail view"""
    try:
        from .models import Customer
        customer = get_object_or_404(Customer, pk=pk)
        return render(request, 'customers/customer_detail.html', {'customer': customer})
    except Exception as e:
        logger.error(f"Customer detail error: {str(e)}")
        return render(request, 'customers/customer_detail.html', {'error': 'Customer not found.'})
