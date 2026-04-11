import csv
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg, F
from django.db.models.functions import TruncDate
from sales.models import Sale, SaleItem
from products.models import Product
from accounts.models import User

@login_required
def daily_sales_report(request, export=False):
    # Requirements: Preview Page Table: Date, Transaction ID, Customer, Cashier, Payment Method, Total Amount
    # Using 'display all available info by default' means we load everything
    sales = Sale.objects.all().select_related('customer', 'user').order_by('-date')
    
    if export:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="daily_sales_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Date', 'Transaction ID', 'Customer', 'Cashier', 'Payment Method', 'Total Amount'])
        for sale in sales:
            customer_name = sale.customer.name if sale.customer else 'Walk-in'
            cashier_name = sale.user.username if sale.user else 'Unknown'
            payment_method = getattr(sale, 'get_payment_method_display', lambda: sale.payment_method)()
            
            writer.writerow([
                sale.date.strftime('%Y-%m-%d %H:%M:%S'),
                sale.id,
                customer_name,
                cashier_name,
                payment_method,
                sale.total_amount
            ])
        return response
    
    return render(request, 'reports/daily_report.html', {'sales': sales})


@login_required
def weekly_sales_report(request, export=False):
    # Requirements: Day, Number of Transactions, Total Revenue
    # Using TruncDate to group transactions by Day as specified in prompt table structure
    data = Sale.objects.annotate(day=TruncDate('date')).values('day').annotate(
        transactions=Count('id'),
        total_revenue=Sum('total_amount')
    ).order_by('-day')
    
    if export:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="weekly_sales_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Day', 'Number of Transactions', 'Total Revenue'])
        for row in data:
            writer.writerow([
                row['day'], 
                row['transactions'], 
                round(row['total_revenue'], 2) if row['total_revenue'] else 0
            ])
        return response

    return render(request, 'reports/weekly_report.html', {'data': data})


@login_required
def product_performance_report(request, export=False):
    # Product Name, Units Sold, Revenue Generated, Current Stock
    data = Product.objects.annotate(
        units_sold=Sum('saleitem__quantity'),
        revenue=Sum(F('saleitem__quantity') * F('saleitem__price'))
    ).order_by('-units_sold')

    if export:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="product_performance_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Product Name', 'Units Sold', 'Revenue Generated', 'Current Stock'])
        for row in data:
            writer.writerow([
                row.product_name,
                row.units_sold or 0,
                round(row.revenue, 2) if row.revenue else 0,
                row.stock_quantity
            ])
        return response

    return render(request, 'reports/product_report.html', {'data': data})


@login_required
def inventory_report(request, export=False):
    # Product Name, Current Stock, Reorder Level, Stock Status (Low / OK)
    products = Product.objects.all().order_by('product_name')
    
    if export:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="inventory_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Product Name', 'Current Stock', 'Reorder Level', 'Stock Status'])
        for p in products:
            status = 'Low' if p.stock_quantity <= p.reorder_level else 'OK'
            writer.writerow([
                p.product_name, 
                p.stock_quantity, 
                p.reorder_level, 
                status
            ])
        return response

    return render(request, 'reports/inventory_report.html', {'products': products})


@login_required
def cashier_sales_report(request, export=False):
    # Cashier Name, Number of Sales, Total Revenue, Average Transaction Value
    data = User.objects.filter(sale__isnull=False).distinct().annotate(
        sales_count=Count('sale'),
        total_rev=Sum('sale__total_amount'),
        avg_trans=Avg('sale__total_amount')
    ).order_by('-total_rev')
    
    if export:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="cashier_sales_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Cashier Name', 'Number of Sales', 'Total Revenue', 'Average Transaction Value'])
        for u in data:
            writer.writerow([
                u.get_full_name() or u.username,
                u.sales_count,
                round(u.total_rev, 2) if u.total_rev else 0,
                round(u.avg_trans, 2) if u.avg_trans else 0
            ])
        return response

    return render(request, 'reports/cashier_report.html', {'data': data})
