from .common import *
import os
import dj_database_url


SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = False
ALLOWED_HOSTS = ['shopit-api.herokuapp.com']
REDIS = os.environ.get('REDIS_URL')
CELERY_BROKER_URL = REDIS

# Paystack production keys go here
PAYSTACK_SECRET_KEY = os.environ.get('PAYSTACK_SECRET_KEY')
PAYSTACK_PUBLIC_KEY = os.environ.get('PAYSTACK_PUBLIC_KEY')

DATABASES = {
    'default': dj_database_url.config()
}

