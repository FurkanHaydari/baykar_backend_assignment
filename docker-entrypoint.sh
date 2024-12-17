#!/bin/bash

# Veritabanının hazır olmasını bekle
echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "Database is up!"

# Migrasyonları uygula
python manage.py migrate

# Initial verileri yükle
python manage.py setup_initial_data

# Development sunucusunu başlat
python manage.py runserver 0.0.0.0:8000
