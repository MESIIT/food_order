# Generated by Django 5.0.3 on 2024-03-30 04:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0029_rename_order_time_order_timestamp_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartitem',
            name='cart',
        ),
        migrations.RemoveField(
            model_name='cartitem',
            name='menu_item',
        ),
        migrations.DeleteModel(
            name='Cart',
        ),
        migrations.DeleteModel(
            name='CartItem',
        ),
    ]
