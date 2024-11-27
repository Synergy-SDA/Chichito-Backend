from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin
from .models import User,OTP

admin.site.register(User)
admin.site.register(OTP)
