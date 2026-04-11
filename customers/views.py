from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from .models import Customer
from django import forms
from django.contrib import messages

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone_number', 'email', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

@login_required
@role_required(['admin', 'manager', 'cashier'])
def customer_list(request):
    query = request.GET.get('q', '')
    if query:
        customers = Customer.objects.filter(name__icontains=query) | Customer.objects.filter(phone_number__icontains=query)
    else:
        customers = Customer.objects.all()
    return render(request, 'customers/list.html', {'customers': customers, 'query': query})

@login_required
@role_required(['admin', 'manager', 'cashier'])
def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer added successfully.")
            return redirect('customers:list')
    else:
        form = CustomerForm()
    return render(request, 'customers/form.html', {'form': form, 'title': 'Add Customer'})

@login_required
@role_required(['admin', 'manager'])
def edit_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer updated successfully.")
            return redirect('customers:list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'customers/form.html', {'form': form, 'title': 'Edit Customer'})
