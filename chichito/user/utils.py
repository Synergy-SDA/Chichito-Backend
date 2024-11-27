import random
from .models import OTP
from django.core.mail import send_mail
from django.utils.timezone import now, timedelta

class OTPService:
    @staticmethod
    def generate_otp(user):
        otp = str(random.randint(100000, 999999))
        OTP.objects.update_or_create(
            user=user,
            defaults={"otp": otp, "expires_at": now() + timedelta(minutes=3)},
        )
        OTPService.send_otp_email(user.mail, otp)

    @staticmethod
    def send_otp_email(mail, otp):
        from django.core.mail import send_mail

        subject = "Verify Your Email"
        message = f"Your OTP code is {otp}. It will expire in 3 minutes."
        from_email = 'noreply.chichito.ir@gmail.com'  # Set your Gmail address
        recipient_list = [mail]

        send_mail(subject, message, from_email, recipient_list)

