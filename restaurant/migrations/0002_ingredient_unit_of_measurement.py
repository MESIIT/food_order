# Generated by Django 5.0.3 on 2024-03-21 05:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredient',
            name='unit_of_measurement',
            field=models.CharField(default='gram', max_length=50),
        ),
    ]