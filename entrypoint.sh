#!/usr/bin/env bash
# Entrypoint script for runtime operations
set -o errexit

echo "Running migrations..."
python manage.py migrate --no-input

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Creating superuser if it doesn't exist..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@pericoTeam.com', 'admin123')
    print('Superuser created: admin / admin123')
else:
    print('Superuser already exists')
END

echo "Loading initial data (products, categories, labels)..."
python manage.py loaddata fixtures/initial_data.json || echo "Fixtures already loaded or not found"

echo "Starting Gunicorn..."
exec gunicorn djecommerce.wsgi:application --bind 0.0.0.0:10000
