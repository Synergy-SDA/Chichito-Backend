# Generated by Django 5.1.3 on 2024-12-13 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_useronetimepassword'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=models.CharField(blank=True, max_length=255, unique=True),
        ),
    ]
