# Generated by Django 5.0 on 2024-01-22 12:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shopapp', '0008_product_created_by'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='created_by',
        ),
    ]
