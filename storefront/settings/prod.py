from .common import *
import os
import dj_database_url


SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = False
ALLOWED_HOSTS = ['shopit-api.herokuapp.com']
REDIS = os.environ.get('REDIS_URL')
CELERY_BROKER_URL = REDIS


DATABASES = {
    'default': dj_database_url.config()
}

