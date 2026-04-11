#!/usr/bin/env python
"""
Test script to check production configuration
"""

import os
import sys
import django

# Test production settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_system.settings_production')

try:
    django.setup()
    print("✅ Production settings loaded successfully")
    
    # Test URLs
    from django.urls import reverse
    try:
        login_url = reverse('accounts:login')
        print(f"✅ Login URL: {login_url}")
    except Exception as e:
        print(f"❌ Login URL error: {e}")
    
    # Test views
    try:
        from accounts.views_production import custom_login_view
        print("✅ Production login view imported successfully")
    except Exception as e:
        print(f"❌ Production login view error: {e}")
    
    # Test database
    from django.db import connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection error: {e}")
    
    print("\n🔍 Configuration Info:")
    print(f"Settings module: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    print(f"DEBUG: {django.conf.settings.DEBUG}")
    print(f"ALLOWED_HOSTS: {django.conf.settings.ALLOWED_HOSTS}")
    
except Exception as e:
    print(f"❌ Production setup failed: {e}")
    sys.exit(1)
