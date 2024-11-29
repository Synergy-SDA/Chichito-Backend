import random
from .models import OTP
from django.core.mail import send_mail
from django.utils.timezone import now, timedelta
class OTPService:
    @staticmethod
    def generate_otp(user, purpose="email_verification"):
        otp = str(random.randint(100000, 999999))
        OTP.objects.update_or_create(
            user=user,
            defaults={"otp": otp, "expires_at": now() + timedelta(minutes=3)},
        )

        
        if purpose == "email_verification":
            OTPService.send_otp_email(user.mail, otp, "Verify Your Email", "Your OTP code for email verification is {}.")
        elif purpose == "password_reset":
            OTPService.send_otp_email(user.mail, otp, "Reset Your Password", "Your OTP code for password reset is {}.")

    @staticmethod
    def send_otp_email(mail, otp, subject, message_template):
        from django.core.mail import send_mail

        message = message_template.format(otp)
        from_email = 'noreply.chichito.ir@gmail.com' 
        recipient_list = [mail]

        send_mail(subject, message, from_email, recipient_list)


