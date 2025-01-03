# Generated by Django 5.1.3 on 2024-12-26 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Order', '0002_alter_order_cart'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='Fname_of_reciever',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='Lname_of_reciever',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='address',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='city',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='email',
            field=models.EmailField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='phone_number',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='postal_code',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='province',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
