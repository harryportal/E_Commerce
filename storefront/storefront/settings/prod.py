from .common import *
import os

SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = False
ALLOWED_HOSTS = []
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'E_Commerce2',
        'USER': 'postgres',
        'PASSWORD': '112233',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}