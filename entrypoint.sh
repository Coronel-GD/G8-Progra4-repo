#!/usr/bin/env bash
# Entrypoint script for runtime operations
set -o errexit

echo "Running migrations..."
python manage.py migrate --no-input

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Starting Gunicorn..."
exec gunicorn djecommerce.wsgi:application --bind 0.0.0.0:10000
