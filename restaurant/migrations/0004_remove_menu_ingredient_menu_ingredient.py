# Generated by Django 5.0.3 on 2024-03-21 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0003_alter_ingredient_unit_of_measurement'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='menu',
            name='ingredient',
        ),
        migrations.AddField(
            model_name='menu',
            name='ingredient',
            field=models.ManyToManyField(blank=True, null=True, to='restaurant.ingredient'),
        ),
    ]
