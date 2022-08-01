from .common import *
import os
DEBUG = True

# Paystack test keys go here
PAYSTACK_SECRET_KEY = os.environ.get('PAYSTACK_SECRET_KEY')
PAYSTACK_PUBLIC_KEY = os.environ.get('PAYSTACK_PUBLIC_KEY')