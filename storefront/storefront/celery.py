""" Configuring celery """
from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storefront.settings')
celery = Celery('storefront')

celery.config_from_object('django.conf:settings', namespace='CELERY')
celery.autodiscover_tasks()