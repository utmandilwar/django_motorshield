from django.core.mail import send_mail
import os

class Util:
    @staticmethod
    def send_email(data):
        send_mail(
            data['subject'],
            data['body'],
            os.environ.get('EMAIL_FROM'),
            [data['to_email']],
            fail_silently=False
        )