from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.validators import MinLengthValidator

import datetime
from django.utils import timezone
from django.utils.timezone import now

class UserManager(BaseUserManager):
    def validate_email(self, email):
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError(_("You must provide a valid email address"))

    def create_user(self, email, password, **extra_fields):
        
        email = self.normalize_email(email)
        self.validate_email(email)
        
        user = self.model( email=email, **extra_fields)
        user.set_password(password)
        user.save(using= self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        
        user = self.create_user( email, password, **extra_fields)
        user.save(using= self._db)
        return user
    
    
class User(AbstractBaseUser, PermissionsMixin):
    class SexChoices(models.TextChoices):
        MALE = 'M', _('مرد')
        FEMALE = 'F', _('زن')
    username = models.CharField(unique=True,
                                max_length=255,
                                validators=[MinLengthValidator(5)])
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(unique=True, max_length=255)
    email = models.EmailField(max_length=255, unique=True, verbose_name=_('Email Address'))
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    password = models.CharField(max_length=255, verbose_name=_('Password'))
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(default=now)   
    sex = models.CharField(max_length=1, choices=SexChoices.choices)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']

    objects = UserManager()
    
    def str(self):
        return self.username
    
    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    

class TempUser(models.Model):
    # username = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    password = models.CharField(max_length=255)
    date_joined = models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=255)
    #ali inja bia username va phone number  to benevis baad to serializer baad verify bbe user asli bede 
    def str(self):
        return self.email
    

class OneTimePassword(models.Model):
    temp_user = models.ForeignKey(TempUser, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, unique=True)

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) 
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 

    def str(self):
        return f"Wallet for {self.user.username}"

    def add_balance(self, amount):
        """Add balance to the wallet"""
        self.balance += amount
        self.save()

    def deduct_balance(self, amount):
        """Deduct balance from the wallet if sufficient funds are available"""
        if self.balance >= amount:
            self.balance -= amount
            self.save()
        else:
            raise ValueError("Insufficient funds in wallet")
        
class UserOneTimePassword(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        
        expiry_time = self.created_at + datetime.timedelta(minutes=4)
        return timezone.now() <= expiry_time
