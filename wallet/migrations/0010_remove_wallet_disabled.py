# Generated by Django 3.0.7 on 2022-06-17 17:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0009_wallet_disabled'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wallet',
            name='disabled',
        ),
    ]