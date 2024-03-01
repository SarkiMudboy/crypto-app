from celery import shared_task
from abstract.email.email import Email

@shared_task()
def send_password_recovery_mail(*args) -> None:

    mail = Email(*args)
    mail.send()