#!/bin/bash
# Start script for Render deployment

echo "Starting application..."

# Wait for database to be ready
echo "Waiting for database..."
python manage.py migrate

# Create superuser if needed
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Superuser created: admin/admin123")
else:
    print("Superuser already exists")
EOF

# Start the application
echo "Starting gunicorn..."
gunicorn pos_system.wsgi:application --bind 0.0.0.0:$PORT
