from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.contrib import messages
from .forms import EmployeeRegistrationForm
from .models import User
from .decorators import role_required
import logging

logger = logging.getLogger(__name__)

def custom_login_view(request):
    """Production-safe login view with comprehensive error handling"""
    try:
        if request.method == 'POST':
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '')
            
            if not username or not password:
                messages.error(request, "Please enter both username and password.")
                return render(request, 'accounts/login.html', {'active_panel': 'login'})
            
            # Try authentication with fallback
            try:
                user = authenticate(request, username=username, password=password)
            except Exception as auth_error:
                logger.error(f"Authentication error: {str(auth_error)}")
                # Fallback: try to get user directly if authentication fails
                try:
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    user = User.objects.get(username=username)
                    if user.check_password(password):
                        login(request, user)
                    else:
                        user = None
                except:
                    user = None
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.username}!")
                    
                    # Safe redirect with multiple fallbacks - prioritize POS pages
                    try:
                        from django.urls import reverse
                        next_url = request.GET.get('next', None)
                        
                        # If no next_url or it's admin, redirect to POS
                        if not next_url or next_url.startswith('/admin/'):
                            next_url = reverse('sales:pos')
                        
                        return redirect(next_url)
                    except:
                        try:
                            return redirect('/sales/pos/')
                        except:
                            return redirect('/admin/')
                else:
                    messages.error(request, "Your account is disabled.")
            else:
                messages.error(request, "Invalid username or password.")
        
        return render(request, 'accounts/login.html', {'active_panel': 'login'})
        
    except Exception as e:
        logger.error(f"Critical login error: {str(e)}")
        # Ultimate fallback - show simple login form
        return render(request, 'accounts/login.html', {
            'active_panel': 'login',
            'error': 'Login system temporarily unavailable. Please try again.'
        })

def register(request):
    """Production-safe registration view"""
    try:
        if request.method == 'POST':
            form = EmployeeRegistrationForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.role = 'cashier'  # Default role for self-registered employees
                user.save()
                login(request, user)
                messages.success(request, f"Account created for {user.username}! Welcome to Hermes Store.")
                
                # Safe redirect
                try:
                    from django.urls import reverse
                    return redirect(reverse('sales:pos'))
                except:
                    return redirect('/admin/')
            else:
                register_errors = []
                for field, errors in form.errors.items():
                    for error in errors:
                        register_errors.append(error)
                return render(request, 'accounts/login.html', {
                    'active_panel': 'register',
                    'register_errors': register_errors
                })
        else:
            return render(request, 'accounts/login.html', {'active_panel': 'register'})
            
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        messages.error(request, "Registration temporarily unavailable. Please try again.")
        return render(request, 'accounts/login.html', {'active_panel': 'register'})

@login_required
@role_required(['admin'])
def employee_list(request):
    """Production-safe employee list view"""
    try:
        employees = User.objects.all().order_by('-date_joined')
        return render(request, 'accounts/employee_list.html', {'employees': employees})
    except Exception as e:
        logger.error(f"Employee list error: {str(e)}")
        messages.error(request, "Unable to load employee list.")
        return redirect('/admin/')

@login_required
@role_required(['admin'])
def employee_role(request, user_id):
    """Production-safe employee role update"""
    try:
        if request.method == 'POST':
            employee = get_object_or_404(User, id=user_id)
            new_role = request.POST.get('role')
            if new_role in ['admin', 'manager', 'cashier']:
                employee.role = new_role
                if new_role == 'admin':
                    employee.is_staff = True
                    employee.is_superuser = True
                else:
                    employee.is_staff = False
                    employee.is_superuser = False
                employee.save()
                messages.success(request, f"Updated role for {employee.username} to {new_role}.")
    except Exception as e:
        logger.error(f"Employee role error: {str(e)}")
        messages.error(request, "Unable to update employee role.")
    return redirect('accounts:employee_list')

@login_required
@role_required(['admin'])
def employee_delete(request, user_id):
    """Production-safe employee deletion"""
    try:
        if request.method == 'POST':
            employee = get_object_or_404(User, id=user_id)
            if employee == request.user:
                messages.error(request, "You cannot delete your own account.")
            else:
                employee.delete()
                messages.success(request, f"Employee {employee.username} has been fired.")
    except Exception as e:
        logger.error(f"Employee delete error: {str(e)}")
        messages.error(request, "Unable to delete employee.")
    return redirect('accounts:employee_list')
