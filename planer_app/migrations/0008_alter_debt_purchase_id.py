# Generated by Django 5.0 on 2024-01-08 00:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planer_app', '0007_alter_purchase_locator_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='debt',
            name='purchase_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='planer_app.purchase'),
        ),
    ]
