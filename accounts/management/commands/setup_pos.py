from django.core.management.base import BaseCommand
from accounts.models import User
from products.models import Product, Category
from customers.models import Customer
import random

class Command(BaseCommand):
    help = 'Seeds the database with initial admin, products, and categories'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")

        # Users
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')
            admin.role = 'admin'
            admin.save()
            self.stdout.write(self.style.SUCCESS("Created superuser: admin (pass: adminpass)"))
        
        if not User.objects.filter(username='manager1').exists():
            manager = User.objects.create_user('manager1', 'manager@example.com', 'managerpass')
            manager.role = 'manager'
            manager.save()
            self.stdout.write(self.style.SUCCESS("Created manager: manager1 (pass: managerpass)"))

        if not User.objects.filter(username='cashier1').exists():
            cashier = User.objects.create_user('cashier1', 'cashier@example.com', 'cashierpass')
            cashier.role = 'cashier'
            cashier.save()
            self.stdout.write(self.style.SUCCESS("Created cashier: cashier1 (pass: cashierpass)"))

        # Categories
        cat_elec, _ = Category.objects.get_or_create(name='Electronics')
        cat_groc, _ = Category.objects.get_or_create(name='Groceries')
        cat_cloth, _ = Category.objects.get_or_create(name='Clothing')

        # Products
        products_data = [
            {'name': 'Wireless Mouse', 'cat': cat_elec, 'price': 25.99, 'stock': 50, 'barcode': '1234567890'},
            {'name': 'Mechanical Keyboard', 'cat': cat_elec, 'price': 89.99, 'stock': 20, 'barcode': '1234567891'},
            {'name': 'Organic Apples (1kg)', 'cat': cat_groc, 'price': 4.50, 'stock': 100, 'barcode': '2234567890'},
            {'name': 'Whole Wheat Bread', 'cat': cat_groc, 'price': 2.99, 'stock': 5, 'barcode': '2234567891'}, # low stock
            {'name': 'Cotton T-Shirt', 'cat': cat_cloth, 'price': 15.00, 'stock': 30, 'barcode': '3234567890'},
        ]

        for p_data in products_data:
            Product.objects.get_or_create(
                product_name=p_data['name'],
                defaults={
                    'category': p_data['cat'],
                    'price': p_data['price'],
                    'stock_quantity': p_data['stock'],
                    'barcode': p_data['barcode'],
                    'supplier': 'Test Supplier Inc.'
                }
            )
        self.stdout.write(self.style.SUCCESS("Created test products."))

        # Customers
        Customer.objects.get_or_create(
            name='John Doe',
            defaults={
                'phone_number': '555-1234',
                'email': 'john@example.com',
                'loyalty_points': 50
            }
        )
        self.stdout.write(self.style.SUCCESS("Created test customer."))

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
