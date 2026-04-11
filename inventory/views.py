from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from products.models import Product
from .models import InventoryLog
from django.contrib import messages

@login_required
@role_required(['admin', 'manager', 'cashier'])
def inventory_list(request):
    low_stock_products = Product.objects.filter(stock_quantity__lte=10)
    all_products = Product.objects.all()
    return render(request, 'inventory/list.html', {
        'low_stock_products': low_stock_products,
        'products': all_products
    })

@login_required
@role_required(['admin'])
def adjust_stock(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        try:
            adjustment = int(request.POST.get('adjustment', 0))
            reason = request.POST.get('reason', '')
            if reason and adjustment != 0:
                product.stock_quantity += adjustment
                product.save()
                
                InventoryLog.objects.create(
                    product=product,
                    user=request.user,
                    quantity_changed=adjustment,
                    reason=reason
                )
                messages.success(request, "Stock adjusted successfully.")
                return redirect('inventory:list')
            else:
                messages.error(request, "Please provide a valid adjustment and reason.")
        except ValueError:
            messages.error(request, "Invalid number.")
    
    return render(request, 'inventory/adjust.html', {'product': product})
