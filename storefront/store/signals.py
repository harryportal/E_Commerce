from django.db.models.signals import post_save
from .models import Customer
from django.dispatch import receiver
from django.conf import settings

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_customer_for_user(sender, **kwargs):
    """ automatically creates a customer once a user is registered """
    if kwargs['created']:
        Customer.objects.create(user=kwargs['instance'])