from django.urls import path
from . import views
from . import views_reports

app_name = 'reports'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('modern/', views.modern_dashboard, name='modern'),
    path('sales/', views.sales_report, name='sales'),
    path('sales/pdf/', views.export_sales_pdf, name='sales_pdf'),
    path('sales/excel/', views.export_sales_excel, name='sales_excel'),
    # Keep the un-requested ones mapped to the old views
    path('profit/', views.profit_report, name='profit'),

    # New Routing mapped to views_reports
    path('daily/', views_reports.daily_sales_report, name='daily_sales'),
    path('daily/export/', views_reports.daily_sales_report, {'export': True}, name='daily_sales_export'),
    
    path('weekly/', views_reports.weekly_sales_report, name='weekly_sales'),
    path('weekly/export/', views_reports.weekly_sales_report, {'export': True}, name='weekly_sales_export'),
    
    path('products/', views_reports.product_performance_report, name='products'),
    path('products/export/', views_reports.product_performance_report, {'export': True}, name='product_performance_export'),
    
    path('inventory/', views_reports.inventory_report, name='inventory'),
    path('inventory/export/', views_reports.inventory_report, {'export': True}, name='inventory_export'),
    
    path('cashiers/', views_reports.cashier_sales_report, name='cashiers'),
    path('cashiers/export/', views_reports.cashier_sales_report, {'export': True}, name='cashier_sales_export'),
]
