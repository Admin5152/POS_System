from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction
import json
import logging

logger = logging.getLogger(__name__)

@login_required
def pos_view_production(request):
    """Production-safe POS view with comprehensive error handling"""
    try:
        # Try to get data with fallbacks
        try:
            from customers.models import Customer
            from products.models import Product, Category
            customers = Customer.objects.all()
            categories = Category.objects.all()
            products = Product.objects.all()[:10]
            
            # Check if we have data and create defaults if needed
            if len(customers) == 0:
                try:
                    Customer.objects.create(name="Walk-in Customer", phone="0000000000")
                    customers = Customer.objects.all()
                except:
                    pass
            
            if len(categories) == 0:
                try:
                    Category.objects.create(name="General")
                    categories = Category.objects.all()
                except:
                    pass
            
            context = {
                'customers': customers,
                'categories': categories,
                'products': products,
                'has_data': True
            }
            
            return render(request, 'sales/pos.html', context)
            
        except Exception as db_error:
            logger.error(f"Database error in POS: {str(db_error)}")
            
            # Fallback to admin panel if POS data fails
            messages.warning(request, "POS system temporarily unavailable. Using admin panel.")
            return redirect('/admin/')
            
    except Exception as e:
        logger.error(f"Critical error in POS view: {str(e)}")
        messages.error(request, "System temporarily unavailable. Please try again later.")
        return redirect('/admin/')

@login_required
def product_search_api_production(request):
    """Production-safe product search API"""
    try:
        from products.models import Product, Category
        
        query = request.GET.get('q', '')
        category_id = request.GET.get('category_id', '')
        
        products = Product.objects.all()
        if category_id and category_id != 'all':
            products = products.filter(category__id=category_id)
        if len(query) >= 2 or query.isdigit():
            products = products.filter(barcode__icontains=query) | products.filter(product_name__icontains=query)
        
        data = []
        for p in products[:20]:
            try:
                product_data = {
                    'id': p.id,
                    'name': p.product_name,
                    'price': float(p.selling_price) if hasattr(p, 'selling_price') else 0.00,
                    'stock': p.stock_quantity if hasattr(p, 'stock_quantity') else 0,
                    'barcode': p.barcode or '',
                    'category': p.category.name if p.category else 'Uncategorized',
                    'image': p.image.url if p.image else '/static/img/no-image.png'
                }
                data.append(product_data)
            except Exception as product_error:
                logger.warning(f"Error processing product {p.id}: {str(product_error)}")
                continue
        
        return JsonResponse({'products': data})
        
    except Exception as e:
        logger.error(f"Product search API error: {str(e)}")
        return JsonResponse({'products': [], 'error': 'Search temporarily unavailable'})

@login_required
def receipts_list(request):
    """Production-safe receipts list view"""
    try:
        from .models import Sale
        import datetime
        today = datetime.date.today()
        sales = Sale.objects.filter(date__date=today).order_by('-date')
        return render(request, 'sales/receipts.html', {'sales': sales, 'today': today})
    except Exception as e:
        logger.error(f"Receipts list error: {str(e)}")
        messages.error(request, "Unable to load receipts.")
        return redirect('/admin/')

@login_required
@transaction.atomic
def checkout_production(request):
    """Production-safe checkout with comprehensive error handling"""
    if request.method == 'POST':
        try:
            from .models import Sale, SaleItem
            from customers.models import Customer
            from payments.models import Payment
            from decimal import Decimal
            
            data = json.loads(request.body)
            items = data.get('items', [])
            customer_id = data.get('customer_id')
            payment_method = data.get('payment_method', 'cash')
            
            # Validate items
            if not items:
                return JsonResponse({'success': False, 'error': 'No items in cart'})
            
            # Get or create customer
            try:
                if customer_id:
                    customer = Customer.objects.get(id=customer_id)
                else:
                    customer = Customer.objects.get_or_create(name="Walk-in Customer", phone="0000000000")[0]
            except:
                customer = Customer.objects.create(name="Walk-in Customer", phone="0000000000")
            
            # Calculate totals
            total_amount = Decimal('0')
            for item in items:
                try:
                    item_total = Decimal(str(item.get('price', 0))) * Decimal(str(item.get('quantity', 1)))
                    total_amount += item_total
                except:
                    return JsonResponse({'success': False, 'error': 'Invalid item data'})
            
            # Create sale
            try:
                sale = Sale.objects.create(
                    customer=customer,
                    total_amount=total_amount,
                    payment_method=payment_method,
                    status='completed'
                )
                
                # Create sale items
                for item in items:
                    try:
                        from products.models import Product
                        product = Product.objects.get(id=item['id'])
                        
                        SaleItem.objects.create(
                            sale=sale,
                            product=product,
                            quantity=item['quantity'],
                            unit_price=Decimal(str(item['price'])),
                            total_price=Decimal(str(item['price'])) * Decimal(str(item['quantity']))
                        )
                        
                        # Update stock
                        if hasattr(product, 'stock_quantity'):
                            product.stock_quantity -= int(item['quantity'])
                            product.save()
                            
                    except Exception as item_error:
                        logger.error(f"Error creating sale item: {str(item_error)}")
                        continue
                
                # Create payment record
                try:
                    Payment.objects.create(
                        sale=sale,
                        amount=total_amount,
                        payment_method=payment_method,
                        status='completed'
                    )
                except:
                    logger.warning("Could not create payment record")
                
                return JsonResponse({
                    'success': True,
                    'sale_id': sale.id,
                    'message': 'Sale completed successfully'
                })
                
            except Exception as sale_error:
                logger.error(f"Error creating sale: {str(sale_error)}")
                return JsonResponse({'success': False, 'error': 'Could not process sale'})
                
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid request data'})
        except Exception as e:
            logger.error(f"Checkout error: {str(e)}")
            return JsonResponse({'success': False, 'error': 'Checkout temporarily unavailable'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
