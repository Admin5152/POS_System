from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from accounts.decorators import role_required
from products.models import Product, Category
from customers.models import Customer
from .models import Sale, SaleItem, Return
from payments.models import Payment
from django.db import transaction
from django.contrib import messages
import json

@login_required
# Allowed for all active staff (admin, manager, cashier)
def pos_view(request):
    customers = Customer.objects.all()
    categories = Category.objects.all()
    return render(request, 'sales/pos.html', {'customers': customers, 'categories': categories})

@login_required
def product_search_api(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category_id', '')
    products = Product.objects.all()
    if category_id and category_id != 'all':
        products = products.filter(category__id=category_id)
    if len(query) >= 2 or query.isdigit():
        products = products.filter(barcode__icontains=query) | products.filter(product_name__icontains=query)
    data = []
    for p in products[:20]:
        data.append({
            'id': p.id,
            'name': p.product_name,
            'price': str(p.price),
            'stock': p.stock_quantity,
            'barcode': p.barcode,
            'category': p.category.name if p.category else 'Uncategorized',
            'image': p.image.url if p.image else None,
        })
    return JsonResponse({'products': data})

@login_required
@transaction.atomic
def checkout(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            items = data.get('items', [])
            customer_id = data.get('customer_id')
            payment_method = data.get('payment_method', 'cash')
            amount_paid = float(data.get('amount_paid', 0))
            
            if not items:
                return JsonResponse({'success': False, 'message': 'Cart is empty'}, status=400)
                
            customer = None
            if customer_id and payment_method == 'card':
                customer = Customer.objects.get(id=customer_id)
                
            # Create Sale
            sale = Sale.objects.create(
                user=request.user,
                customer=customer,
                payment_method=payment_method,
                total_amount=0 # Will update after items
            )
            
            total = 0
            for item in items:
                product = Product.objects.get(id=item['id'])
                qty = int(item['quantity'])
                if product.stock_quantity < qty:
                    raise Exception(f"Not enough stock for {product.product_name}")
                
                # Deduct stock
                product.stock_quantity -= qty
                product.save()
                
                # Add Sale Item
                price = product.price
                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=qty,
                    price=price
                )
                total += float(price) * qty
                
            sale.total_amount = total
            sale.save()
            
            # Loyalty Points Update
            if customer:
                customer.loyalty_points += int(total // 10)
                customer.save()
                
            # Create Payment Record
            Payment.objects.create(
                sale=sale,
                payment_method=payment_method,
                amount=total # Optionally calculate exact amount paid vs change
            )
            
            return JsonResponse({'success': True, 'sale_id': sale.id})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

@login_required
def receipt_view(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    return render(request, 'sales/receipt.html', {'sale': sale})

@login_required
def receipts_list(request):
    import datetime
    today = datetime.date.today()
    sales = Sale.objects.filter(date__date=today).order_by('-date')
    return render(request, 'sales/receipts.html', {'sales': sales, 'today': today})

@login_required
@role_required(['admin', 'manager', 'cashier'])
def process_return(request):
    items = None
    error_msg = None
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'search':
            barcode = request.POST.get('barcode', '').strip()
            if barcode:
                # Find recent SaleItems matching this barcode
                items = SaleItem.objects.filter(product__barcode=barcode).order_by('-sale__date')[:5]
                if not items.exists():
                    error_msg = "No recent purchases found for this barcode."
            else:
                error_msg = "Please enter a valid barcode."
                
        elif action == 'process_return':
            item_id = request.POST.get('sale_item_id')
            reason = request.POST.get('reason')
            
            try:
                sale_item = SaleItem.objects.get(id=item_id)
                # Check if it was already returned
                if hasattr(sale_item, 'returns') and sale_item.returns.exists():
                    messages.error(request, "This item has already been returned.")
                else:
                    Return.objects.create(
                        sale_item=sale_item,
                        reason=reason,
                        refund_amount=sale_item.price * sale_item.quantity
                    )
                    # Re-add to stock (optional based on policy, but doing it here)
                    if sale_item.product:
                        sale_item.product.stock_quantity += sale_item.quantity
                        sale_item.product.save()
                    messages.success(request, f"Return processed successfully for Sale #{sale_item.sale.id}.")
            except SaleItem.DoesNotExist:
                messages.error(request, "Sale item not found.")
                
    return render(request, 'sales/returns.html', {'items': items, 'error_msg': error_msg})
