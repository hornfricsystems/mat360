# Generated by Django 3.1.2 on 2021-07-13 10:49

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sacco_manager', '0002_auto_20210704_0906'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vcontrol',
            name='time_available_by_driver',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 13, 10, 49, 18, 628142)),
        ),
    ]