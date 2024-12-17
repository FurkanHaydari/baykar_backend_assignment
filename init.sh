#!/bin/bash

# Migrasyonları uygula
echo "Applying migrations..."
python manage.py migrate

# Initial verileri yükle
echo "Loading initial data..."
python manage.py setup_initial_data

echo "Setup completed!"
