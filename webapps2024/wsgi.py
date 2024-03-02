"""
WSGI config for webapps2024 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from create_admin_account import create_admin_group_and_account

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapps2024.settings')

application = get_wsgi_application()

# Creates the admin account and group on startup

create_admin_group_and_account()

