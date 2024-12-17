"""
WSGI config for uav_production project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uav_production.settings')

application = get_wsgi_application()
