# Generated by Django 5.0.3 on 2024-03-25 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0008_billpayment_foodpreparation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='menu',
        ),
        migrations.AddField(
            model_name='order',
            name='menu',
            field=models.ManyToManyField(to='restaurant.menu'),
        ),
    ]
