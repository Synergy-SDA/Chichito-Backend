# Generated by Django 5.0.7 on 2024-11-16 04:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_alter_featurevalue_feature'),
    ]

    operations = [
        migrations.AlterField(
            model_name='featurevalue',
            name='feature',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='values', to='product.feature'),
        ),
    ]