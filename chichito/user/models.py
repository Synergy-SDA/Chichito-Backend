from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone

from django.utils.translation import gettext_lazy as _

class CustomUserManager (BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):

        if not email:
            return ValueError(_('وارد کردن ایمیل الزامی است'))

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user
    
class User(AbstractBaseUser):

    class SexChoices(models.TextChoices):
        MALE = 'M', _('مرد')
        FEMALE = 'F', _('زن')

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(unique=True, max_length=255)
    mail = models.EmailField(unique=True, max_length=255)
    birth_date = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    sex = models.CharField(max_length=1, choices=SexChoices.choices)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone_number' 
    REQUIRED_FIELDS = ['first_name', 'last_name']  

   
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name

    def age(self):
        if self.birth_date:
            from datetime import date
            return date.today().year - self.birth_date.year
        return None

    def save(self, *args, **kwargs):
        if not self.id:  
            self.last_login = timezone.now()
        super().save(*args, **kwargs)   


