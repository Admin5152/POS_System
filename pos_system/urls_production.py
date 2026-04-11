"""
Production URL Configuration for POS System
Uses production-safe views with comprehensive error handling
"""

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def home_redirect(request):
    """Safe home redirect - prioritize POS pages"""
    try:
        from django.urls import reverse
        return redirect('sales:pos')
    except:
        try:
            return redirect('/sales/pos/')
        except:
            return redirect('/admin/')

def debug_info(request):
    """Debug endpoint to check configuration"""
    return JsonResponse({
        'settings_module': request.META.get('DJANGO_SETTINGS_MODULE', 'unknown'),
        'root_urlconf': __name__,
        'debug': settings.DEBUG,
        'allowed_hosts': settings.ALLOWED_HOSTS,
        'database_engine': settings.DATABASES['default']['ENGINE'],
        'render_env': 'RENDER' in settings.__dict__
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_redirect, name='home'),
    path('debug/', debug_info, name='debug_info'),
    path('accounts/', include('accounts.urls_production')),
    path('sales/', include('sales.urls_production')),
    path('reports/', include('reports.urls')),
    path('products/', include('products.urls_production')),
    path('inventory/', include('inventory.urls_production')),
    path('customers/', include('customers.urls_production')),
    path('payments/', include('payments.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
