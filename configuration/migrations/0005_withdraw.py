# Generated by Django 3.0.7 on 2022-06-20 09:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuration', '0004_currency_buy_rate'),
    ]

    operations = [
        migrations.CreateModel(
            name='Withdraw',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('max', models.FloatField()),
                ('min', models.FloatField()),
            ],
        ),
    ]
