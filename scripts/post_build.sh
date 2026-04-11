#!/bin/bash
# Post-build script for Render deployment

echo "Running post-build deployment tasks..."

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist
echo "Creating superuser if needed..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Superuser created: admin/admin123")
else:
    print("Superuser already exists")
EOF

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Post-build tasks completed!"
