# Generated by Django 5.1.3 on 2024-11-08 16:13

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='username',
            field=models.CharField(default='salam', max_length=255, unique=True, validators=[django.core.validators.MinLengthValidator(5)]),
        ),
    ]