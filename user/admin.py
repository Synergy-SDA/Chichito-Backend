from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin
from .models import *

admin.site.register(User)
admin.site.register(Wallet)

