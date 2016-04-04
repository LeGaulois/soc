"""
WSGI config for soc project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

from django.core.wsgi import get_wsgi_application
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "soc.settings")

os.environ["LC_LANG"] = 'fr_FR.UTF-8'
os.environ["LANG"] = 'fr_FR.UTF-8'
os.environ["LC_ALL"] = 'fr_FR.UTF-8'
application = get_wsgi_application()
