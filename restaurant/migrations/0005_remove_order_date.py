# Generated by Django 5.0.3 on 2024-03-21 17:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0004_remove_menu_ingredient_menu_ingredient'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='date',
        ),
    ]
