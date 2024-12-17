"""
ASGI config for uav_production project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uav_production.settings')

application = get_asgi_application()
