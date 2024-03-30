# Generated by Django 5.0.3 on 2024-03-27 19:08

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0018_alter_order_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_items', models.CharField(max_length=5000)),
                ('name', models.CharField(default='', max_length=50)),
                ('bill_total', models.IntegerField()),
                ('phone', models.CharField(max_length=10)),
                ('bill_time', models.DateTimeField()),
            ],
        ),
        migrations.AddField(
            model_name='menu',
            name='list_order',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='order',
            name='bill_clear',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='order_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='order',
            name='price',
            field=models.CharField(default='0', max_length=5),
        ),
        migrations.DeleteModel(
            name='CartItem',
        ),
    ]