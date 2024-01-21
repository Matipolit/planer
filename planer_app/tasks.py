from celery import shared_task
from django.core.mail import send_mail
from planer import settings


@shared_task(bind=True)
def sendEmail(self, mailTo: str, message: str, subject: str):
    print("My recipient is: " + mailTo)
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[mailTo],
        fail_silently=False,
    )
    return "Done"
