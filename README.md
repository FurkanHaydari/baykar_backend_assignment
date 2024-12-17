# İHA (UAV) Production Management System

This project is a UAV Production Management System built with Django. It manages the production of various UAV models including TB2, TB3, AKINCI, and KIZILELMA.

## Features

- Personnel login system
- Team management (Wing, Body, Tail, Avionics, Assembly teams)
- Part production and inventory management
- Assembly management
- Stock tracking and warnings
- Production history tracking

## Technical Stack

- Python
- Django
- PostgreSQL
- Django Rest Framework
- Bootstrap
- Django Crispy Forms

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure PostgreSQL database settings in .env file
5. Run migrations:
   ```bash
   python manage.py migrate
   ```
6. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```
7. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Project Structure

- `uav_production/` - Main project directory
- `production/` - Main application
- `accounts/` - User authentication and team management
- `api/` - REST API endpoints
