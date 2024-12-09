from email.message import EmailMessage
import random

import smtplib
import secrets
from .models import *
from django.conf import settings

def send_otp_email(email):
    from_email = settings.EMAIL_HOST_USER
    password = settings.EMAIL_HOST_PASSWORD

    otp = random.randint(100000, 999999)

    
    temp_user = TempUser.objects.get(email=email)
    OneTimePassword.objects.create(temp_user=temp_user, otp=otp)
    
    subject = 'One Time Password'
    body = f'Thanks for registering on freediscussion.ir.\nYour One Time Password is {otp}' 
    
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = email
    msg.set_content(body)
    with smtplib.SMTP_SSL('smtp.gmail.com',465) as server:
        server.login(from_email, password)
        server.send_message(msg)
def send_otp_to_user_email(user):
    from_email = settings.EMAIL_HOST_USER
    password = settings.EMAIL_HOST_PASSWORD

    otp = random.randint(100000, 999999)

    
    UserOneTimePassword.objects.create(user=user, otp=otp)

    subject = 'Password Reset OTP'
    body = f'Your OTP for resetting your password is {otp}. This OTP is valid for 4 minutes.'

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = user.email
    msg.set_content(body)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(from_email, password)
        server.send_message(msg)
