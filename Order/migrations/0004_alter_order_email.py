# Generated by Django 5.1.3 on 2024-12-26 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Order', '0003_order_fname_of_reciever_order_lname_of_reciever_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='email',
            field=models.EmailField(max_length=255, null=True),
        ),
    ]