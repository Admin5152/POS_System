#!/bin/bash
# Build script for Render deployment

echo "Starting build process..."

# Install dependencies
pip install -r requirements-render.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

echo "Build process completed!"
