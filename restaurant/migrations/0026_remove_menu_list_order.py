# Generated by Django 5.0.3 on 2024-03-29 11:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0025_alter_transaction_timestamp'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='menu',
            name='list_order',
        ),
    ]
