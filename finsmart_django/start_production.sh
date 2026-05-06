#!/bin/bash
set -e

cd /home/runner/workspace/finsmart_django

echo "=== Running migrations ==="
python manage.py migrate --run-syncdb

echo "=== Seeding categories ==="
python manage.py seed_categories

echo "=== Creating test user ==="
python manage.py create_test_user

echo "=== Creating admin superuser ==="
python manage.py create_superuser_auto

echo "=== Collecting static files ==="
python manage.py collectstatic --noinput

echo "=== Starting gunicorn on port $PORT ==="
exec gunicorn finsmart.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --timeout 120 \
    --log-level info \
    --access-logfile - \
    --error-logfile -
