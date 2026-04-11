from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from .models import Product, Category
from django import forms
from django.contrib import messages

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'category', 'price', 'cost_price', 'stock_quantity', 'barcode', 'supplier', 'image']
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'barcode': forms.TextInput(attrs={'class': 'form-control'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

@login_required
@role_required(['admin', 'manager', 'cashier'])
def product_list(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('cat', 'all')
    categories = Category.objects.all()
    products = Product.objects.select_related('category').all()
    if query:
        products = products.filter(product_name__icontains=query) | products.filter(barcode__icontains=query)
    if category_id and category_id != 'all':
        products = products.filter(category__id=category_id)
    return render(request, 'products/list.html', {
        'products': products.distinct(),
        'query': query,
        'categories': categories,
        'active_cat': category_id,
    })

@login_required
@role_required(['admin'])
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product added successfully.")
            return redirect('products:list')
    else:
        form = ProductForm()
    return render(request, 'products/form.html', {'form': form, 'title': 'Add Product'})

@login_required
@role_required(['admin'])
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully.")
            return redirect('products:list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/form.html', {'form': form, 'title': 'Edit Product'})

@login_required
@role_required(['admin'])
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted successfully.")
        return redirect('products:list')
    return render(request, 'products/delete.html', {'product': product})
