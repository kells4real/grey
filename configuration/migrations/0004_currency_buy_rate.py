# Generated by Django 3.0.7 on 2022-06-03 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuration', '0003_auto_20220601_1648'),
    ]

    operations = [
        migrations.AddField(
            model_name='currency',
            name='buy_rate',
            field=models.FloatField(default=0.0),
        ),
    ]