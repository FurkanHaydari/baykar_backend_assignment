#!/bin/bash

# Django settings modülünü ayarla
export DJANGO_SETTINGS_MODULE=uav_production.settings

# Veritabanının hazır olmasını bekle
echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "Database is up!"

# Migrasyonları uygula
echo "Applying migrations..."
python manage.py migrate

# Initial verileri yükle
echo "Loading initial data..."
python manage.py setup_initial_data

# Testleri çalıştır
echo "Running tests..."
PYTHONPATH=/app python manage.py test production.tests.ProductionTests --verbosity=2

# Development sunucusunu başlat
echo "Starting development server..."
python manage.py runserver 0.0.0.0:8000
