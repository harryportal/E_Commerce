from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_mail(subject, message, sender, to):
    """ a backgroung tasks to send mail to client upon registration or password
    reset email"""
    send_mail(subject=subject, message=message, from_email=sender,
              recipient_list=to)
