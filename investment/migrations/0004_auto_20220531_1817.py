# Generated by Django 3.0.7 on 2022-05-31 17:17

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('investment', '0003_auto_20220531_1018'),
    ]

    operations = [
        migrations.AddField(
            model_name='investment',
            name='last_profit_date',
            field=models.DateTimeField(default=datetime.datetime(2022, 5, 31, 17, 17, 59, 216522, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='portfolio',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
