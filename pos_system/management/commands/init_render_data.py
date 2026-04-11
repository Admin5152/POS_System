from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

class Command(BaseCommand):
    help = 'Initialize data for Render deployment'

    def handle(self, *args, **options):
        User = get_user_model()
        
        try:
            with transaction.atomic():
                # Create admin user if it doesn't exist
                if not User.objects.filter(username='admin').exists():
                    admin = User.objects.create_user(
                        username='admin',
                        email='admin@pos-system.com',
                        password='admin123',
                        first_name='Admin',
                        last_name='User',
                        role='admin',
                        is_staff=True,
                        is_superuser=True
                    )
                    self.stdout.write(self.style.SUCCESS('✅ Created admin user: admin/admin123'))
                else:
                    self.stdout.write(self.style.SUCCESS('✅ Admin user already exists'))
                
                # Create basic data if needed
                try:
                    from products.models import Category
                    if not Category.objects.exists():
                        Category.objects.create(name="General")
                        Category.objects.create(name="Clothing")
                        Category.objects.create(name="Electronics")
                        self.stdout.write(self.style.SUCCESS('✅ Created default categories'))
                except:
                    self.stdout.write(self.style.WARNING('⚠️ Could not create categories'))
                
                try:
                    from customers.models import Customer
                    if not Customer.objects.exists():
                        Customer.objects.create(
                            name="Walk-in Customer",
                            phone="0000000000",
                            email="walkin@pos-system.com"
                        )
                        self.stdout.write(self.style.SUCCESS('✅ Created default customer'))
                except:
                    self.stdout.write(self.style.WARNING('⚠️ Could not create customer'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error initializing data: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('🎉 Render data initialization completed!'))
