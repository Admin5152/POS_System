from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.contrib import messages
from .forms import EmployeeRegistrationForm
from .models import User
from .decorators import role_required

def custom_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next', 'sales:pos')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'accounts/login.html', {
        'active_panel': 'login'
    })

def register(request):
    if request.method == 'POST':
        form = EmployeeRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'cashier' # Default role for self-registered employees
            user.save()
            login(request, user)
            messages.success(request, f"Account created for {user.username}! Welcome to Hermes Store.")
            return redirect('sales:pos')
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

@login_required
@role_required(['admin'])
def employee_list(request):
    employees = User.objects.all().order_by('-date_joined')
    return render(request, 'accounts/employee_list.html', {'employees': employees})

@login_required
@role_required(['admin'])
def employee_role(request, user_id):
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
    return redirect('accounts:employee_list')

@login_required
@role_required(['admin'])
def employee_delete(request, user_id):
    if request.method == 'POST':
        employee = get_object_or_404(User, id=user_id)
        if employee == request.user:
            messages.error(request, "You cannot delete your own account.")
        else:
            employee.delete()
            messages.success(request, f"Employee {employee.username} has been fired.")
    return redirect('accounts:employee_list')
