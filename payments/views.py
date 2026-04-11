from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from django.db import transaction
from django.contrib import messages
import requests
import json
import uuid

from sales.models import Sale, SaleItem
from products.models import Product
from customers.models import Customer
from .models import Payment

@login_required
def initialize_payment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            items = data.get('items', [])
            customer_id = data.get('customer_id')
            payment_method = 'paystack'
            
            if not items:
                return JsonResponse({'success': False, 'message': 'Cart is empty'}, status=400)
            
            # Recalculate total
            total = 0
            for item in items:
                product = Product.objects.get(id=item['id'])
                qty = int(item['quantity'])
                if product.stock_quantity < qty:
                    return JsonResponse({'success': False, 'message': f'Not enough stock for {product.product_name}'}, status=400)
                total += float(product.price) * qty
            
            customer = None
            if customer_id:
                try:
                    customer = Customer.objects.get(id=customer_id)
                except Customer.DoesNotExist:
                    pass
            
            # Store pending sale in session
            request.session['pending_sale'] = {
                'items': items,
                'customer_id': customer_id,
                'payment_method': payment_method,
                'total_amount': total
            }
            
            url = "https://api.paystack.co/transaction/initialize"
            headers = {
                "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
                "Content-Type": "application/json",
            }
            
            # Generate unique reference
            ref = str(uuid.uuid4())
            callback_url = request.build_absolute_uri(f'/payments/paystack/verify/{ref}/')
            
            email = "customer@email.com"
            if customer and getattr(customer, 'email', None):
                email = customer.email

            payload = {
                "email": email,
                "amount": int(total * 100),  # Paystack uses kobo
                "reference": ref,
                "callback_url": callback_url
            }

            try:
                response = requests.post(url, json=payload, headers=headers, timeout=10)
                res_data = response.json()
                if res_data.get('status'):
                    return JsonResponse({'success': True, 'authorization_url': res_data['data']['authorization_url']})
                else:
                    return JsonResponse({'success': False, 'message': res_data.get('message', 'Failed to initialize payment')})
            except requests.exceptions.RequestException:
                # Network Error Case
                return JsonResponse({'success': False, 'message': 'Network error while contacting Paystack. Please try again later.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

@login_required
def verify_payment(request, reference):
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        res_data = response.json()
    except requests.exceptions.RequestException:
        # Network Error Case
        messages.error(request, "Network error verifying payment. Please check your transaction status.")
        return redirect('sales:pos')

    if res_data.get("status") and res_data.get("data", {}).get("status") == "success":
        # Payment successful check if already handled
        if Payment.objects.filter(transaction_reference=reference).exists():
            messages.info(request, "This payment has already been verified.")
            return redirect('sales:pos')

        # Session Expired Case
        pending_sale = request.session.get('pending_sale')
        if not pending_sale:
            messages.error(request, "Session expired or sale data lost. Payment was successful but cart data couldn't be found.")
            return redirect('sales:pos')

        items = pending_sale.get('items', [])
        customer_id = pending_sale.get('customer_id')
        payment_method = pending_sale.get('payment_method', 'paystack')
        total = pending_sale.get('total_amount', 0)

        customer = None
        if customer_id:
            try:
                customer = Customer.objects.get(id=customer_id)
            except Customer.DoesNotExist:
                pass

        try:
            with transaction.atomic():
                sale = Sale.objects.create(
                    user=request.user,
                    customer=customer,
                    payment_method=payment_method,
                    total_amount=total
                )

                for item in items:
                    product = Product.objects.get(id=item['id'])
                    qty = int(item['quantity'])
                    
                    product.stock_quantity -= qty
                    product.save()

                    SaleItem.objects.create(
                        sale=sale,
                        product=product,
                        quantity=qty,
                        price=product.price
                    )

                if customer and hasattr(customer, 'loyalty_points'):
                    customer.loyalty_points += int(total // 10)
                    customer.save()

                Payment.objects.create(
                    sale=sale,
                    payment_method=payment_method,
                    amount=total,
                    transaction_reference=reference,
                    status='success'
                )

            # Clear session
            del request.session['pending_sale']
            
            messages.success(request, "Payment successful! Receipt generated.")
            
            # In order to use reverse properly, we use redirect
            # We redirect to the receipt view that already exists in sales
            from django.urls import reverse
            return redirect(reverse('sales:receipt', kwargs={'sale_id': sale.id}))

        except Exception as e:
            messages.error(request, f"Error completing sale: {str(e)}")
            return redirect('sales:pos')

    else:
        # Payment failed, abandoned, or invalid reference
        messages.error(request, "Payment failed, was abandoned, or reference is invalid. Please try again.")
        return redirect('sales:pos')
